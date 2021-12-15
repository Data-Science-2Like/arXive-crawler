from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from datetime import datetime
import metaCrawler as meta
import dataCrawler as data
import expander as exp
import argparse

import asyncio


def get_records():
    meta.get_records(datetime.now(),datetime.now())


def get_data():
    asyncio.run(data.getData("C:\\Users\\Simon\\Desktop\\ai_papers"))


def expand_latex():
    exp.extractLatex("C:\\Users\\Simon\\Desktop\\ai_papers", "C:\\Users\\Simon\\Desktop\\ai_papers\\latex")

if __name__ == '__main__':
    parent_parser = argparse.ArgumentParser()
    parent_parser.add_argument('--out', '-o', default= '.', help='output directory')
    parent_parser.add_argument('--debug', default=False, required=False, help='debug flag')
    main_parser = argparse.ArgumentParser()
    meta_subparsers = main_parser.add_subparsers(title="metadata", dest="metadata_command")
    meta_parser = meta_subparsers.add_parser("meta", help="collect metadata", parents=[parent_parser])

    ## meta options


    download_parsers = main_parser.add_subparsers(title="download", dest="download_command")
    download_parser = download_parsers.add_parser("download", help="download raw data", parents=[parent_parser])
