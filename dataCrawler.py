import time
import os
import io
import asyncio
import aiohttp
from os import path
from counter import Counter

from database import initDatabase,getPaperUrls, commit, getPaperUrlsByCategory

exportUrl = "export.arxiv.org"
burstSize = 4
sleepLength = 1

def replaceUrl(url):
    return url.replace("arxiv.org",exportUrl).replace('abs','e-print')

async def getData(dest):

    #check if destination folder exists else create
    if not path.exists(dest):
        os.mkdir(dest)

    paperCounter = Counter("Crawled {0} papers this minute. Average: {1}")

    metaData = getPaperUrlsByCategory([10,62,122],200110617)
    requestCount = 0
    try:
        while requestCount < len(metaData):
            currUrls = list()
            for i in range(0,burstSize):
                record = metaData[requestCount]
                requestCount+= 1
                url = replaceUrl(record[2])
                currUrls.append((url,record[0]))

            async with aiohttp.ClientSession() as session:
                ret = await asyncio.gather(*[downloadPaper(dest,url,id, session) for (url, id) in currUrls])

            paperCounter.increment(burstSize)
            time.sleep(sleepLength)
    except BaseException as err:
        print("Error oucurred after ", requestCount, " requests with burstSize: ", burstSize, " and sleepLength: ", sleepLength)
        raise


def checkSignature(buffer):
    # guess the filetype based on the beginning of the buffer
    tarSig1 = bytearray([0x1F,0x8B,0x08, 0x08])
    tarSig2 = bytearray([0x1F, 0x8B, 0x08, 0x00])

    pdfSig = bytearray("%PDF".encode())
    if tarSig1 == buffer or tarSig2 == buffer:
        return '.tar.gz'
    elif pdfSig == buffer:
        return '.pdf'
    else:
        raise ValueError("Unknown File Signature")


async def downloadPaper(dest,url, identifier, session):

    # taken from https://stackoverflow.com/questions/57126286/fastest-parallel-requests-in-python
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            ext = checkSignature(resp[0:4])
            if response.status != 200:
                print("error on url: ", url)
                if response.status == 403:
                    print("Seems like we got blocked :(")
                    raise Exception(str("Error ") + str(response.status))

            savePath = os.path.join(dest, str(identifier) + ext)
            open(savePath, 'wb').write(resp)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))

    # fileType = magic.from_buffer(data, mime=True)
    # print(fileType)
    # libmagic for windows not so easy :(

    # print("Signature: " , data.content[0:4])




