from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from datetime import datetime
import metaCrawler as meta
import dataCrawler as data
import expander as exp
import jsonExporter as json
import statstics as stat
import argparse

import asyncio

if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument('--out', '-o', default='.', help='output directory')
    main_parser.add_argument('--debug', default=False, required=False, help='debug flag', action='store_true')
    cmd_parsers = main_parser.add_subparsers(title="commands", dest="command")

    ## meta options
    meta_parser = cmd_parsers.add_parser("meta", help="collect metadata")
    meta_parser.add_argument('--from', default=datetime.now(), required=False, help='start date for metadata')
    meta_parser.add_argument('--until', default=datetime.now(), required=False, help='end date for metadata')


    # download options
    download_parser = cmd_parsers.add_parser("download", help="download raw data")
    download_parser.add_argument('--sleep', default=2, required=False, help='sleep time between two burst')
    download_parser.add_argument('--burst', default=4, required=False, help='size of one reading burst')
    download_parser.add_argument('--start', default=0, required=False, help='the start id of the papers which are going to be crawled')
    download_parser.add_argument('--end', default=3000000000, required=False, help='the end id of the papers which are going to be crawled')
    download_parser.add_argument('--proxy', default=False, required=False, help='allows the use of proxys when connection gets blocked', action='store_true')
    download_parser.add_argument('--diff', default=False, required=False, help='rescans the directory before starting crawling to determine which files already have been downloaded', action='store_true')

    # expander options
    expand_parser = cmd_parsers.add_parser("expand", help="expand files")
    expand_parser.add_argument('--in','-i', help='input data directory')
    expand_parser.add_argument('--bib', default=False, required=False, help='also extract bib resources', action='store_true')
    expand_parser.add_argument('--start', default=0, required=False,
                            help='the start id of the papers which are going to be expanded')

    # zip options
    zip_parser = cmd_parsers.add_parser("zip", help="zips to metadata file")
    zip_parser.add_argument('--name', default="ids.json", required=False, help='The name of the file to which the ids get exported')

    # count options
    count_parser = cmd_parsers.add_parser("count", help="counts statistics for dataset")
    count_parser.add_argument('--in', '-i', help='input data directory')



    args = main_parser.parse_args()
    arguments = vars(args)
    used_command =  arguments["command"]
    if "meta" == used_command:
        meta.get_records(arguments["from"],arguments["until"], arguments["debug"])

    elif "download" == used_command:
        asyncio.run(data.getData(arguments["out"], arguments["start"], arguments["end"],int(arguments["sleep"]), int(arguments["burst"]), arguments["proxy"], arguments["diff"]))

    elif "expand" == used_command:
        exp.extractLatex(arguments["in"], arguments["out"], arguments["debug"], arguments["bib"], int(arguments["start"]))

    elif "zip" == used_command:
        json.exportDownload(arguments["out"], arguments["name"])
    elif "count" == used_command:
        stat.count_ocurrences(arguments["in"])
    else:
        main_parser.print_help()
