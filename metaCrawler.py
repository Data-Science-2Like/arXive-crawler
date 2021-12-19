from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

from database import initDatabase, insertPaper, commit

def get_records(von, bis, debug):

    URL = 'http://export.arxiv.org/oai2'

    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    registry
    client = Client(URL, registry)

    initDatabase()
    count = 0
    for (id,meta,_) in client.listRecords(metadataPrefix='oai_dc', set='cs'):
        count += 1
        insertPaper(str(meta.getField('identifier')[0]).split('/')[-1].replace('.',''),meta.getField('title'),meta.getField('creator'), meta.getField('subject'), meta.getField('date'), meta.getField('identifier'))
        if count % 100 == 0:
            commit()
            print("fetched ", count, " documents")
    commit()
    # for record in client.listRecords(metadataPrefix='oai_dc'):
    #     print(record)
