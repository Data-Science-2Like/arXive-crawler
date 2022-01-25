import json
import os
from TexSoup import TexSoup
from database import get_paper_info_from_title
from tqdm import tqdm
import re


def get_key(string):
    middle = list()
    cmds = re.split('[|]', string)
    words = re.split('{|}', cmds[-1])

    if len(words) < 2:
        return ""
    return words[-2]

def detex(string):
    middle = list()
    cmds = re.split('[|]', string)
    words = re.split('{|}', cmds[-1])

    for word in words:
        more_words = word.split(" ")
        for mword in more_words:
            if mword.startswith("\\"):
                continue
            middle.append(mword.replace("\n",""))
    return " ".join(middle)

def extract_bibliography(filename):
    bibliograpy = list()
    #bib = TexSoup(open(filename), tolerance=1)
    bib = open(filename)
    item = dict()
    count = 0
    for line in bib:

        if line.startswith("\\bibitem"):
            if len(item) > 0 and 'key' in item and 'title' in item and len(item['title']) > 3:
                bibliograpy.append(item)
            item = dict()
            count = 0

            key = get_key(line)
            item['key'] = key

        if count == 1:
            item['authors'] = detex(line)
        if count == 2:
            item['title'] = detex(line)
        count += 1
    return bibliograpy


def extract_citation(filename):
    directory = os.path.dirname(filename)

    citation_info = list()
    idStr = os.path.basename(filename).split(".")[0]

    if not os.path.exists(os.path.join(directory,str(idStr + ".bbl"))):
        return list()

    soup = TexSoup(open(filename), tolerance=1)

    bibliography = extract_bibliography(os.path.join(directory,str(idStr + ".bbl")))

    sec_citation_list = list(soup.find_all(['cite', 'section']))

    curSec = ''
    bibCount = 0
    dbCount = 0
    bibInfo = list()
    for elem in sec_citation_list:
        if elem.name == 'section':
            curSec = elem.string
        else:
            # find entry in bib file
            matches = [x for x in bibliography if elem.string in x['key']]
            if len(matches) == 0:
                continue
            bibCount += 1
            bibInfo.append(matches[0])
            # query against metadata database
            paper_info = get_paper_info_from_title(matches[0]['title'])


            if len(paper_info) > 0:
                dbCount += 1
                m = {'id' : idStr, 'section': curSec, 'cite': paper_info[0]['id']}
                citation_info.append(m)
    print("Found in bib file: ", str(bibCount), " , found in database: ", str(dbCount))
    return citation_info, bibInfo

def extractLatex(source):
    citation_info = list()
    bib_info = list()
    files = os.listdir(source)
    files.reverse()
    for filename in tqdm(files):
        if filename.endswith("tex"):
            try:
                new_cite_info, new_bib_info  = extract_citation(os.path.join(source,filename))
                citation_info = citation_info + new_cite_info
                bib_info = bib_info + new_bib_info
                print(f"Extracted {filename} successfully. Added {len(new_cite_info)} entries" )
            except Exception as e:
                print(f"Doc {filename} could not be loaded.")
                print("Error occured: " + str(e))

    print(len(citation_info))
    with open(os.path.join(source, "citation_info.json"), 'w', encoding='utf-8') as f:
        json.dump(citation_info,f, ensure_ascii=False, indent=4)

    with open(os.path.join(source, "bib_info.json"), 'w', encoding='utf-8') as f:
        json.dump(bib_info,f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    extractLatex('D:\expanded')
