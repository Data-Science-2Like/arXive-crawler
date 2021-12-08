from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from datetime import datetime
import metaCrawler as meta
import dataCrawler as data
import expander as exp

import asyncio


def get_records():
    meta.get_records(datetime.now(),datetime.now())


def get_data():
    asyncio.run(data.getData("C:\\Users\\Simon\\Desktop\\ai_papers"))


def expand_latex():
    exp.extractLatex("C:\\Users\\Simon\\Desktop\\ai_papers", "C:\\Users\\Simon\\Desktop\\ai_papers\\latex")

if __name__ == '__main__':
    expand_latex()
