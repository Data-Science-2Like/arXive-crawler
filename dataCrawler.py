import time
import os
import io
import requests
from os import path
from counter import Counter

from database import initDatabase,getPaperUrls, commit, getPaperUrlsByCategory

exportUrl = "export.arxiv.org"
burstSize = 4
sleepLength = 1

def replaceUrl(url):
    return url.replace("arxiv.org",exportUrl).replace('abs','e-print')

def getData(dest):

    #check if destination folder exists else create
    if not path.exists(dest):
        os.mkdir(dest)

    paperCounter = Counter("Crawled {0} papers this minute.")

    metaData = getPaperUrlsByCategory([10,62,122],200000000)
    requestCount = 0
    try:
        for record in metaData:
            requestCount+= 1

            # make request and download raw files
            url = replaceUrl(record[2])
            # print(url)
            downloadPaper(dest, url, record[0])

            paperCounter.increment()

            if requestCount % burstSize == 0:
                time.sleep(1)
    except BaseException as err:
        print("Error oucurred after ", requestCount, " requests with burstSize: ", burstSize, " and sleepLength: ", sleepLength)
        raise


def checkSignature(buffer):
    # guess the filetype based on the beginning of the buffer
    tarSig = bytearray([0x1F,0x8B,0x08, 0x08])
    if tarSig == buffer :
        return '.tar.gz'
    else:
        return '.pdf'


def downloadPaper(dest,url, identifier):

    data = requests.get(url, allow_redirects=True)
    if data.status_code != 200:
        print("error on url: ", url)
        if data.status_code == 403:
            print("Seems like we got blocked :(")
        raise Exception(str("Error ") + str(data.status_code))

    # fileType = magic.from_buffer(data, mime=True)
    # print(fileType)
    # libmagic for windows not so easy :(

    ext = checkSignature(data.content[0:4])

    savePath = os.path.join(dest, str(identifier) + ext)
    open(savePath, 'wb').write(data.content)



