from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from datetime import datetime
import metaCrawler as meta
import dataCrawler as data
import expander as exp
import argparse

import asyncio


def get_records(von, bis):
    meta.get_records(von,bis)


def get_data():
    asyncio.run(data.getData("C:\\Users\\Simon\\Desktop\\ai_papers"))


def expand_latex():
    exp.extractLatex("C:\\Users\\Simon\\Desktop\\ai_papers", "C:\\Users\\Simon\\Desktop\\ai_papers\\latex")

if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument('--out', '-o', default='.', help='output directory')
    main_parser.add_argument('--debug', default=False, required=False, help='debug flag')
    cmd_parsers = main_parser.add_subparsers(title="commands", dest="command")

    ## meta options
    meta_parser = cmd_parsers.add_parser("meta", help="collect metadata")
    meta_parser.add_argument('--from', default=datetime.now(), required=False, help='start date for metadata')
    meta_parser.add_argument('--until', default=datetime.now(), required=False, help='end date for metadata')


    # download options
    download_parser = cmd_parsers.add_parser("download", help="download raw data")



    # expander options
    expand_parser = cmd_parsers.add_parser("expand", help="expand files")
    expand_parser.add_argument('--in','-i', help='input data directory')
    expand_parser.add_argument('--bib', default=False, required=False, help='also extract bib resources')

    args = main_parser.parse_args()
    arguments = vars(args)
    used_command =  arguments["command"]
    if "meta" == used_command:
        meta.get_records(arguments["from"],arguments["until"], arguments["debug"])

    elif "download" == used_command:
        asyncio.run(data.getData(arguments["out"]))

    elif "expander" == used_command:
        exp.extractLatex(arguments["in"], arguments["out"], arguments["debug"], arguments["bib"])
    else:
        main_parser.print_help()
