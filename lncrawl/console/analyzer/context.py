# -*- coding: utf-8 -*-

import inspect
import os
import re
from enum import IntEnum, auto
from urllib.parse import urlparse

import click
from bs4 import BeautifulSoup, Tag
from slugify import slugify

from lncrawl.app import Language
from lncrawl.app.browser import Browser, BrowserResponse


class Selector(IntEnum):
    novel_name = auto()


class AnalyzerContext:
    def __init__(self):
        self.browser = Browser()
        self.url: str = None
        self.response: BrowserResponse = None
        self.soup: BeautifulSoup = None
        self.scraper_name: str = None
        self.scraper_path: str = None
        self.novel_language: Language = Language.ENGLISH
        self._selectors = dict()

    def _get_globals(self) -> dict:
        return dict(inspect.getmembers(self))

    def _get_commands(self) -> list:
        return ['help', 'view']

    def assign(self, name: str, selector: str) -> None:
        self._selectors[name] = selector

    def view(self, name: str = None) -> str:
        return '\n'.join([
            '%s = %s' % (
                click.style(s.name, fg='green'),
                self._selectors.get(s, 'None')
            )
            for s in iter(Selector)
            if not name or s.name == name
        ])

    def set_url(self, value: str) -> None:
        '''Change current url'''
        click.echo('GET ' + click.style(value, fg='cyan', bold=True))
        self.response = self.browser.get(value)
        _status = f'{self.response.raw.status_code} - {self.response.raw.reason}'
        click.echo('Status: ' + click.style(_status, fg='green'))
        click.echo()

        self.url = value
        self.soup = self.response.soup

        host = str(urlparse(value).hostname)
        click.echo(f'host = {host}')

        _name = re.sub(r'[^a-zA-Z0-9]+', '_', host)
        self.scraper_name = ''.join([
            c[0].upper() + c[1:]
            for c in _name.split('_')
        ])
        click.echo(f'scraper_name = {self.scraper_name}')

        self.scraper_path = slugify(host, max_length=30) + '.py'
        if self.novel_language != Language.UNKNOWN:
            self.scraper_path = os.path.join(
                self.novel_language, self.scraper_path)
        click.echo(f'scraper_path = {self.scraper_path}')

    def locate(self, text: str) -> str:
        '''Find css selector for a text'''
        text = text.lower().strip()
        selectors = {
            self.get_selector(node.parent): str(node)
            for node in self.soup.find_all(
                string=re.compile(text, flags=re.IGNORECASE),
                recursive=True
            )
        }
        if not selectors:
            return 'Found no matching selectors.'
        result = f'Found {len(selectors)} matching selector(s):\n'
        result += '\n'.join([
            ' > '.join([
                click.style(k, fg='green', bold=True),
                click.style(v, fg='white', dim=True),
            ]) for k, v in selectors.items()
        ])
        return result

    def get_selector(self, node: Tag) -> str:
        '''Get unique css selector of a node'''
        if not node or node.name == '[document]':
            return ''
        if node.name in ['body', 'main']:
            return node.name
        if node.has_attr('id'):
            return '#' + node['id']
        current = '.'.join([node.name] + node.get_attribute_list('class', []))
        return (self.get_selector(node.parent) + ' ' + str(current)).strip()

    def help(self) -> str:
        methods = []
        variables = []
        for key, val in inspect.getmembers(self):
            val = getattr(self, key)
            styled_key = click.style(key, fg='green', bold=True)
            if inspect.isbuiltin(val) or key[0] == '_':
                continue
            if inspect.ismethod(val):
                args = str(inspect.signature(val))
                args = click.style(args, dim=True)
                docs = inspect.getdoc(val)
                docs = '\n- ' + str(docs) if docs else ''
                methods.append(f"{styled_key}{args}{docs}")
            else:
                type_name = type(val).__name__
                val = str(val)
                if len(val) > 160:
                    val = '%s ...(%d more lines)' % (val[:150], len(val) - 150)
                variables.append(f"{styled_key}:{type_name} = {val}")

        message = ''

        message += click.style(('=' * 20) + '\n', fg='white', dim=True)
        message += click.style('Methods:\n', bold=True)
        message += click.style(('=' * 20) + '\n', fg='white', dim=True)
        message += '\n'.join(methods) + '\n\n'

        message += click.style(('=' * 20) + '\n', fg='white', dim=True)
        message += click.style('Variables:\n', bold=True)
        message += click.style(('=' * 20) + '\n', fg='white', dim=True)
        message += '\n'.join(variables) + '\n\n'

        return message
