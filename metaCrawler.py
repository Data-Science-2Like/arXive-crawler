from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

from database import initDatabase, insertPaper

def get_records():

    URL = 'http://export.arxiv.org/oai2'

    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    registry
    client = Client(URL, registry)

    initDatabase()

    for (id,meta,_) in client.listRecords(metadataPrefix='oai_dc', set='cs'):
        insertPaper(str(meta.getField('identifier')[0]).split('/')[-1].replace('.',''),meta.getField('title'),meta.getField('creator'), meta.getField('subject'), meta.getField('date'), meta.getField('identifier'))

    # for record in client.listRecords(metadataPrefix='oai_dc'):
    #     print(record)
