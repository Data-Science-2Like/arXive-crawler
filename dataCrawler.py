import time
import os
import io
import requests
from os import path
import pyfsig as sig

from database import initDatabase,getPaperUrls, commit

exportUrl = "export.arxiv.org"
burstSize = 4
sleepLength = 1

def replaceUrl(url):
    return url.replace("arxiv.org",exportUrl).replace('abs','e-print')

def getData(dest):

    #check if destination folder exists else create
    if not path.exists(dest):
        os.mkdir(dest)

    metaData = getPaperUrls()

    requestCount = 0
    for record in metaData:
        requestCount+= 1

        # make request and download raw files
        url = replaceUrl(record[2])
        # print(url)
        downloadPaper(dest, url, record[0])

        if requestCount % burstSize == 0:
            time.sleep(1)


def downloadPaper(dest,url, identifier):

    #rawPage = requests.get(url)
    #if (rawPage.status_code != 200):
    #    print("error on url: ", url)

    #soup = BeautifulSoup(rawPage.content, 'html.parser')

    data = requests.get(url, allow_redirects=True)

    fileType = sig.get_from_file(io.BytesIO(data.content))

    # fileType = magic.from_buffer(data, mime=True)
    # print(fileType)
    # libmagic for windows not so easy :(




    savePath = os.path.join(dest, str(identifier) + ".tar.gz")
    open(savePath, 'wb').write(data.content)

