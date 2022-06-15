import json
import time
import os
import io
import asyncio
import re
from enum import Enum
from pathlib import Path
from random import random, choice

import pandas as pd

import aiohttp
from os import path

import requests

from counter import Counter

from database import initDatabase, getPaperUrls, commit, getPaperUrlsByCategory

exportUrl = "export.arxiv.org"


def replaceUrl(url, use_proxy):
    return url.replace("arxiv.org", exportUrl).replace('abs', 'e-print').replace('http', 'https')


def get_proxy_list():
    # from https://stackoverflow.com/questions/48426624/scraping-free-proxy-listing-website
    resp = requests.get('https://free-proxy-list.net/')
    df = pd.read_html(resp.text)[0]
    return df[(df['Https'] == 'yes') & (df['Anonymity'] == 'elite proxy')]


def get_proxy(proxy_list, use):
    if not use:
        return ""
    idx = int(random() * len(proxy_list))
    proxy_str = "http://" + str(proxy_list.iat[idx, 0]) + ":" + str(proxy_list.iat[idx, 1])
    return proxy_str


def get_ids_from_disk(dest):
    ids = list()
    for filename in os.listdir(dest):
        # now readin ids from json file
        if (filename.endswith("json")):
            with open(os.path.join(dest, filename), 'r', encoding='utf-8') as f:
                more_ids = json.load(f)
                for id in more_ids:
                    if id.endswith("tar.gz"):
                        ids.append(int(Path(Path(id).stem).stem))
                    elif id == 'arxiv_metadate':
                        continue
                    else:
                        ids.append(int(id))
                continue

        # otherwise it must be raw data
        stemmed = Path(filename).stem
        # double stemming because stem only removes on extension
        if filename.endswith("tar.gz"):
            stemmed = Path(stemmed).stem
        ids.append(int(stemmed))
    return ids


def fetch_ordered(job_queue, completed):
    job_queue.sort()
    completed.sort()

    remaining = []
    idx_jobs = 0
    idx_c = 0
    while (idx_jobs < len(job_queue) and idx_c < len(completed)):
        if job_queue[idx_jobs][0] == completed[idx_c]:
            idx_jobs += 1
            idx_c += 1
            continue
        if job_queue[idx_jobs][0] > completed[idx_c]:
            idx_c += 1
            continue
        if job_queue[idx_jobs][0] < completed[idx_c]:
            remaining.append(job_queue[idx_jobs])
            idx_jobs += 1
            continue
    while (idx_jobs < len(job_queue)):
        remaining.append(job_queue[idx_jobs])
        idx_jobs += 1

    return remaining


async def getData(dest, start_id, stop_id, sleepLength, burstSize, proxy, diff):
    # check if destination folder exists else create
    if not path.exists(dest):
        os.mkdir(dest)

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36'
    ]
    user_agent = choice(user_agents)
    # headers = {'User-Agent': user_agent}

    paperCounter = Counter("Crawled {0} papers this minute. Average: {1}")

    job_queue = getPaperUrlsByCategory([10, 62, 122], start_id, stop_id)
    already_existing_ids = list()

    if diff:
        already_existing_ids = get_ids_from_disk(dest)
        old = len(job_queue)
        print("Fetching already existing paper entries. Found ", len(already_existing_ids))
        job_queue = fetch_ordered(job_queue, already_existing_ids)
        print("Skipping ", old - len(job_queue), " entries")

    print("Beginning to crawl ", len(job_queue), " papers")
    requestCount = 0
    curr_proxy = str()
    proxy_list = []
    if proxy:
        proxy_list = get_proxy_list()
    try:
        while requestCount < len(job_queue):
            currUrls = list()
            for i in range(0, burstSize):
                record = job_queue[requestCount]
                requestCount += 1
                url = replaceUrl(record[2], len(curr_proxy) > 4)
                currUrls.append((url, record[0], record))

            newProxyNeeded = False
            # async with aiohttp.ClientSession() as session:
            #    ret = await asyncio.gather(*[downloadPaper(dest, url, id, session, get_proxy(proxy_list, len(curr_proxy) > 4), r) for (url, id,r) in currUrls])
            #    for status, st_record in ret:
            #        if status is not Status.OK:
            #            job_queue.append(st_record)
            #            print("Adding {} again to list to query it later".format(st_record[0]))
            #            newProxyNeeded = True
            #        if status is Status.OK:
            #            paperCounter.increment(1)
            for (url, id, r) in currUrls:
                status, st_record = await downloadPaperLegacy(dest, url, id, r)
                if status is not Status.OK:
                    job_queue.append(st_record)
                    print("Adding {} again to list to query it later".format(st_record[0]))
                    newProxyNeeded = False
                if status is Status.OK:
                    paperCounter.increment(1)
            time.sleep(sleepLength)

            if newProxyNeeded and proxy:
                # get new proxy
                proxy_list = get_proxy_list()
                idx = int(random() * len(proxy_list))
                curr_proxy = "http://" + str(proxy_list.iat[idx, 0]) + str(":") + str(proxy_list.iat[idx, 1])
                # print("Now using proxy ", curr_proxy)
                print("Got new proxy list")

            if newProxyNeeded and not proxy:
                raise Exception("Seems like we got blocked consider activating the proxy option")


    except BaseException as err:
        print("Error oucurred after ", requestCount, " requests with burstSize: ", burstSize, " and sleepLength: ",
            sleepLength)
        raise


def checkSignature(buffer):
    # guess the filetype based on the beginning of the buffer
    tarSig1 = bytearray([0x1F, 0x8B, 0x08, 0x08])
    tarSig2 = bytearray([0x1F, 0x8B, 0x08, 0x00])

    tarSigs = [bytearray([0x1F, 0x8B, 0x08, 0x08]), bytearray([0x1F, 0x8B, 0x08, 0x00])]

    wordSig = b'PK\x03\x04'
    pdfSig = bytearray("%PDF".encode())
    if buffer in tarSigs:
        return '.tar.gz'
    elif wordSig == buffer:
        return '.docx'
    elif pdfSig == buffer:
        return '.pdf'

    else:
        return '.test'
        raise ValueError("Unknown File Signature")


async def downloadPaperLegacy(dest, url, identifier, tuple):
    r = requests.get(url)
    if r.status_code == 200:
        ext = checkSignature(r.content[0:4])
        savePath = os.path.join(dest, str(identifier) + ext)
        open(savePath, 'wb').write(r.content)
        return Status.OK, tuple
    else:
        return Status.ERROR, tuple



async def downloadPaper(dest, url, identifier, session, proxy, tuple):
    # taken from https://stackoverflow.com/questions/57126286/fastest-parallel-requests-in-python
    try:
        if len(proxy) > 4:
            async with session.get(url=url, proxy=proxy, max_redirects=10, allow_redirects=True,
                                   timeout=10) as response:
                resp = await response.read()
                # First check if response was successfully
                if response.status != 200:
                    print("error on url: ", tuple)
                    if response.status == 403:
                        print("Seems like we got blocked :(")
                        raise BlockedConnection()
                    return Status.ERROR, tuple
                else:
                    ext = checkSignature(resp[0:4])
                    savePath = os.path.join(dest, str(identifier) + ext)
                    open(savePath, 'wb').write(resp)
                    return Status.OK, tuple
        else:
            async with session.get(url=url) as response:
                resp = await response.read()
                # First check if response was successfully
                if response.status != 200:
                    print("error on url: ", url)
                    if response.status == 403:
                        print("Seems like we got blocked :(")
                        raise BlockedConnection()
                    return Status.ERROR, tuple
                else:
                    ext = checkSignature(resp[0:4])
                    savePath = os.path.join(dest, str(identifier) + ext)
                    open(savePath, 'wb').write(resp)
                    return Status.OK, tuple
    except BlockedConnection as e:
        print("Unable to get url {} because the access is blocked".format(url))
        return Status.BLOCKED, tuple
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))
        return Status.ERROR, tuple


class Status(Enum):
    OK = 0,
    ERROR = 1,
    BLOCKED = 2


class BlockedConnection(Exception):
    pass
