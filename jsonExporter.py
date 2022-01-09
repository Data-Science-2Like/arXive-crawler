import os
import json
from os import path
from pathlib import Path

from database import getPaperUrls, getPaperUrlsByCategory

def exportJson(dest):

    #check if destination folder exists else create
    if not path.exists(dest):
        os.mkdir(dest)


    metaData = getPaperUrlsByCategory([10,62,122],200000000)
    print("Entrycount: ", len(metaData))
    jsonData = list()
    for record in metaData:
        jsonEntry = { 'id': record[0] , 'title': record[1], 'url': record[2], 'datetime': record[3]}
        jsonData.append(jsonEntry)

    with open(os.path.join(dest, "metaData.json"), 'w', encoding='utf-8') as f:
        json.dump(jsonData,f, ensure_ascii=False, indent=4)


def _get_ids_from_disk(dest):
    ids = list()
    for filename in os.listdir(dest):
        # skip json files
        if (filename.endswith("json")):
            continue

        stemmed = Path(filename).stem
        # double stemming because stem only removes on extension
        if filename.endswith("tar.gz"):
            stemmed = Path(stemmed).stem
        ids.append(stemmed)
    return ids


def exportDownload(dest, filename):
    # exports all ids already existing in the current directory to an json file for easy communication
    # between different crawler instances

    if not path.exists(dest):
        print("Could not locate directory")
        return

    ids = _get_ids_from_disk(dest)

    with open(os.path.join(dest, filename), 'w', encoding='utf-8') as f:
        json.dump(ids, f, ensure_ascii=False, indent=4)








def export():
    exportJson("C:\\Users\\Simon\\Desktop\\ai_papers")


if __name__ == '__main__':
    export()