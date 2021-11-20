from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

def print_hi(name):

    print(f'Hi, {name}')

    URL = 'http://export.arxiv.org/oai2'

    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(URL, registry)

    for record in client.listRecords(metadataPrefix='oai_dc'):
        print(record)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
