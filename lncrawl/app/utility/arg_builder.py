# -*- coding: utf-8 -*-

from argparse import ArgumentParser, _ActionsContainer
from typing import Dict, List, Tuple, Union

ArgListType = Union[List, Dict, Tuple]


def _build_args(parser: _ActionsContainer, arguments: ArgListType):
    for kwarg in arguments:
        if isinstance(kwarg, dict):
            args = kwarg.pop('args', tuple())
            if isinstance(args, tuple):
                args = list(args)
            elif not isinstance(args, list):
                args = [args]
            parser.add_argument(*args, **kwarg)
        elif isinstance(kwarg, list):
            group = parser.add_argument_group()
            _build_args(group, kwarg)
        elif isinstance(kwarg, tuple):
            mutex = parser.add_mutually_exclusive_group()
            _build_args(mutex, list(kwarg))
        else:
            raise ValueError(f"{type(kwarg)}[{kwarg}]")


class SubParser:
    def __init__(self, name: str, help: str, args: ArgListType = [], **kwargs):
        self.args = args
        kwargs['name'] = name
        kwargs['help'] = help
        self.kwargs = kwargs


def create_parser(args: ArgListType = [],
                  commands: List[SubParser] = [],
                  **kwargs) -> ArgumentParser:
    parser = ArgumentParser(**kwargs)
    _build_args(parser, args)

    if commands:
        subparsers = parser.add_subparsers(
            title='Commands',
            help='Available commands',
        )
        for command in commands:
            sub = subparsers.add_parser(**command.kwargs)
            _build_args(sub, command.args)

    return parser
