# -*- coding: utf-8 -*-
import os
import sys
from argparse import Namespace

from .utility import ModuleUtils
from .utility.arg_builder import SubParser, create_parser

# Use a dictionary to add new argument
# Use tuple for mutually exclusive group
# Use list for a simple group
_parser = create_parser(
    epilog='~' * 78,
    # usage="lnc [options...]\n"
    # "       lncrawl [options...]\n"
    # "       lightnovel-crawler [options...]"
    args=[
        dict(args=('-v', '--version'), action='version',
             version='Lightnovel Crawler ' + ModuleUtils.get_version()),
        dict(args=('-c, --config'), dest='config', metavar='CONFIG_FILE',
             help='The config file path'),
    ],
    commands=[
        SubParser(
            name='scraper',
            help="Download ebooks given an URL or query",
            args=[
                (
                    dict(args=('-s, --source_url'), dest='source', metavar='URL',
                         help='URL to get chapter list of a novel'),
                    dict(args=('-q, --query'), dest='query', metavar='TEXT',
                         help='A query to search for novels'),
                )
            ]
        ),
        SubParser(
            name='analyze',
            help="Process an URL and generate scraper",
            args=[
                dict(args=('-s, --source_url'), dest='source', metavar='URL',
                     help='URL to get chapter list of a novel'),
            ]
        )
    ],
)


_parsed_args = None


def get_args() -> Namespace:
    args = sys.argv[1:]
    if os.getenv('MODE') == 'TEST':
        args = []

    global _parser, _parsed_args
    if _parsed_args is None:
        _parsed_args = _parser.parse_args(args)
    return _parsed_args
