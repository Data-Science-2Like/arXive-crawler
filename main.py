from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from datetime import datetime
import metaCrawler as meta
import dataCrawler as data

import asyncio

def get_records():

    meta.get_records(datetime.now(),datetime.now())
    ## URL = 'http://export.arxiv.org/oai2'

    #registry = MetadataRegistry()
    #registry.registerReader('oai_dc', oai_dc_reader)
    #registry
    ##client = Client(URL, registry)

    ##for (id,meta,_) in client.listRecords(metadataPrefix='oai_dc', set='cs'):
    ##    print(meta.getField('title'))

    # for record in client.listRecords(metadataPrefix='oai_dc'):
    #     print(record)

def get_data():
    asyncio.run(data.getData("C:\\Users\\Simon\\Desktop\\ai_papers"))


if __name__ == '__main__':
    get_data()