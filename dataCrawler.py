import time
import os
import io
import asyncio
import re
from enum import Enum
from random import random

import pandas as pd

import aiohttp
from os import path

import requests

from counter import Counter

from database import initDatabase, getPaperUrls, commit, getPaperUrlsByCategory

exportUrl = "export.arxiv.org"


def replaceUrl(url,use_proxy):
    return url.replace("arxiv.org", exportUrl).replace('abs', 'e-print')

def get_proxy_list():
    # from https://stackoverflow.com/questions/48426624/scraping-free-proxy-listing-website
    resp = requests.get('https://free-proxy-list.net/')
    df = pd.read_html(resp.text)[0]
    return df[(df['Https'] == 'yes') & (df['Anonymity'] == 'elite proxy')]

def get_proxy(proxy_list, use):
    if not use:
        return ""
    idx = int(random() * len(proxy_list))
    proxy_str = "http://" + str(proxy_list.iat[idx,0]) + ":" + str(proxy_list.iat[idx,1])
    return proxy_str

async def getData(dest, start_id, sleepLength, burstSize):
    # check if destination folder exists else create
    if not path.exists(dest):
        os.mkdir(dest)

    paperCounter = Counter("Crawled {0} papers this minute. Average: {1}")

    metaData = getPaperUrlsByCategory([10, 62, 122], start_id)
    requestCount = 0
    curr_proxy = str()
    proxy_list = get_proxy_list()
    try:
        while requestCount < len(metaData):
            currUrls = list()
            for i in range(0, burstSize):
                record = metaData[requestCount]
                requestCount += 1
                url = replaceUrl(record[2],len(curr_proxy) > 4)
                currUrls.append((url, record[0]))

            newProxyNeeded = False
            async with aiohttp.ClientSession() as session:
                ret = await asyncio.gather(*[downloadPaper(dest, url, id, session, get_proxy(proxy_list, len(curr_proxy) > 4)) for (url, id) in currUrls])
                for status, st_url in ret:
                    if status is not Status.OK:
                        metaData.append(st_url)
                        print("Adding {} again to list to query it later".format(st_url))
                        newProxyNeeded = True
                    if status is Status.OK:
                        paperCounter.increment(1)
            time.sleep(sleepLength)

            if newProxyNeeded:
                # get new proxy
                proxy_list = get_proxy_list()
                idx = int(random() * len(proxy_list))
                curr_proxy = "http://" + str(proxy_list.iat[idx,0]) + str(":") + str(proxy_list.iat[idx,1])
                # print("Now using proxy ", curr_proxy)
                print("Got new proxy list")
    except BaseException as err:
        print("Error oucurred after ", requestCount, " requests with burstSize: ", burstSize, " and sleepLength: ",
              sleepLength)
        raise


def checkSignature(buffer):
    # guess the filetype based on the beginning of the buffer
    tarSig1 = bytearray([0x1F, 0x8B, 0x08, 0x08])
    tarSig2 = bytearray([0x1F, 0x8B, 0x08, 0x00])

    pdfSig = bytearray("%PDF".encode())
    if tarSig1 == buffer or tarSig2 == buffer:
        return '.tar.gz'
    elif pdfSig == buffer:
        return '.pdf'
    else:
        raise ValueError("Unknown File Signature")


async def downloadPaper(dest, url, identifier, session, proxy):
    # taken from https://stackoverflow.com/questions/57126286/fastest-parallel-requests-in-python
    try:
        if len(proxy) > 4:
            async with session.get(url=url, proxy=proxy, max_redirects=10, allow_redirects=True, timeout=10) as response:
                resp = await response.read()
                # First check if response was successfully
                if response.status != 200:
                    print("error on url: ", url)
                    if response.status == 403:
                        print("Seems like we got blocked :(")
                        raise BlockedConnection()
                    return Status.ERROR, url
                else:
                    ext = checkSignature(resp[0:4])
                    savePath = os.path.join(dest, str(identifier) + ext)
                    open(savePath, 'wb').write(resp)
                    return Status.OK, url
        else:
            async with session.get(url=url) as response:
                resp = await response.read()
                # First check if response was successfully
                if response.status != 200:
                    print("error on url: ", url)
                    if response.status == 403:
                        print("Seems like we got blocked :(")
                        raise BlockedConnection()
                    return Status.ERROR, url
                else:
                    ext = checkSignature(resp[0:4])
                    savePath = os.path.join(dest, str(identifier) + ext)
                    open(savePath, 'wb').write(resp)
                    return Status.OK, url
    except BlockedConnection as e:
        print("Unable to get url {} because the access is blocked".format(url))
        return Status.BLOCKED, url
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))
        return Status.ERROR, url


class Status(Enum):
    OK = 0,
    ERROR = 1,
    BLOCKED = 2


class BlockedConnection(Exception):
    pass
