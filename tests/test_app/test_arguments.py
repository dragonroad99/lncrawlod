# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentError

import pytest

from lncrawl.app.utility import create_parser


class TestArguments:

    def test_build_arguments(self):
        parser = create_parser(
            args=[
                dict(args=('-v', '--version'), action='version', version='1.0'),
                dict(args=('--config')),
            ]
        )
        cfg = parser.parse_args(['--config', 'some file'])
        assert cfg.config == 'some file'

    def test_value_error(self):
        with pytest.raises(ValueError):
            create_parser(args=[
                ('bad value'),
                dict(args=('--config')),
            ])

    def test_argument_group(self):
        parser = create_parser(args=[
            dict(args=('-v', '--version'), action='version', version='1.0'),
            [
                dict(args=('--group')),
                dict(args=('--arg')),
                dict(args=('--more')),
            ]
        ])
        arg = parser.parse_args(['--group', 'one'])
        assert arg.group == 'one'
        assert arg.arg is None
        arg = parser.parse_args(['--arg', 'two'])
        assert arg.group is None
        assert arg.arg == 'two'
        arg = parser.parse_args(['--group', 'one', '--arg', 'two'])
        assert arg.group == 'one'
        assert arg.arg == 'two'

    def test_mutually_exclusive_argument(self):
        parser = create_parser(args=[
            dict(args=('-v', '--version'), action='version', version='1.0'),
            (
                dict(args=('--mututally')),
                dict(args=('--exclusive')),
                dict(args=('--more')),
            )
        ])
        arg = parser.parse_args(['--mututally', 'one'])
        assert arg.mututally == 'one'
        assert arg.exclusive is None
        arg = parser.parse_args(['--exclusive', 'two'])
        assert arg.mututally is None
        assert arg.exclusive == 'two'
        with pytest.raises(SystemExit):
            with pytest.raises(ArgumentError):
                # disable error log from parser
                setattr(parser, 'error', lambda x: sys.exit())
                # parse invalid mutex group
                parser.parse_args(['--mututally', 'one', '--exclusive', 'two'])

    def test_duplicate_arguments(self):
        with pytest.raises(ArgumentError):
            create_parser(args=[
                dict(args=('-v', '--version'), action='version', version='1.0'),
                dict(args=('--aaarg')),
                dict(args=('--aaarg')),
            ])

    def test_multi_level_of_hierarchy(self):
        create_parser(args=[
            dict(args=('-v', '--version'), action='version', version='1.0'),
            (
                dict(args=('--mututally')),
                dict(args=('--exclusive')),
            ),
            dict(args=('--padded')),
            [
                dict(args=('--group')),
                dict(args=('--arg')),
                (
                    dict(args=('--mututal_in_group')),
                    dict(args=('--exclusive_in_group')),
                    [
                        dict(args=('--inner_group')),
                        dict(args=('--inner_arg')),
                    ]
                ),
            ],
            dict(args=('--more')),
            [
                dict(args='--another'),
                dict(args='--group_2'),
            ]
        ])

    def test_args_with_list_and_single_values(self):
        create_parser(args=[
            dict(args='--single'),
            dict(args=('--bracket')),
            dict(args=('-m', '--multi')),
        ])

    def test_args_with_non_str_values(self):
        with pytest.raises(TypeError):
            create_parser(args=[
                dict(args=3),
            ])
