# -*- coding: utf-8 -*-

import inspect
import json
import os
import re
from enum import IntEnum, auto
from urllib.parse import urlparse

import click
from bs4 import BeautifulSoup, Tag
from slugify import slugify

from lncrawl import sources
from lncrawl.app import Language, ModuleUtils
from lncrawl.app.browser import Browser, BrowserResponse


class Selector(IntEnum):
    novel_name = auto()
    novel_author = auto()
    novel_cover = auto()
    novel_details = auto()
    chapter_content = auto()


class AnalyzerContext:
    def __init__(self):
        self.browser = Browser()
        self.url: str = None
        self.response: BrowserResponse = None
        self.soup: BeautifulSoup = None
        self.scraper_url: str = None
        self.scraper_name: str = None
        self.scraper_path: str = None
        self.novel_language: Language = Language.ENGLISH
        self._selectors = dict()

    def _get_globals(self) -> dict:
        return dict(inspect.getmembers(self))

    def _get_commands(self) -> list:
        return [f.__name__ for f in [
            self.view,
            self.help,
            self.generate,
        ]]

    def save(self, name: str, selector: str) -> None:
        '''Set a selector for generator'''
        self._selectors[name] = selector

    def view(self, name: str = None) -> str:
        '''Check list of all available selector names'''
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

        _parsed = urlparse(value)
        host = str(_parsed.hostname)
        click.echo(f'host = {host}')

        self.scraper_url = f"{_parsed.scheme}://{_parsed.hostname}/"
        click.echo(f'scraper_url = {self.scraper_url}')

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
        '''Shows this message'''
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
        message += click.style('Variables:\n', bold=True)
        message += click.style(('=' * 20) + '\n', fg='white', dim=True)
        message += '\n'.join(variables)

        message += '\n\n'

        message += click.style(('=' * 20) + '\n', fg='white', dim=True)
        message += click.style('Methods:\n', bold=True)
        message += click.style(('=' * 20) + '\n', fg='white', dim=True)
        message += '\n'.join(methods)

        return message

    def generate(self):
        '''Genrate source file with current selectors'''
        def get_css(x):
            return "%s" % json.dumps(self._selectors.get(x, ''))

        code = f'''# -*- coding: utf-8 -*-

from lncrawl.app import (Author, AuthorType, Chapter, Context, Language,
                         SoupUtils, TextUtils, UrlUtils, Volume)
from lncrawl.app.scraper import Scraper


class {self.scraper_name}(Scraper):
    version: int = 1
    base_urls = ['{self.scraper_url}']

    def login(self, ctx: Context) -> bool:
        pass

    def fetch_info(self, ctx: Context) -> None:
        soup = self.get_sync(ctx.toc_url).soup

        ctx.language = Language.ENGLISH

        # Parse novel
        ctx.novel.name = SoupUtils.select_value(soup, {get_css(Selector.novel_name)})
        ctx.novel.name = TextUtils.ascii_only(ctx.novel.name)

        ctx.novel.cover_url = SoupUtils.select_value(soup, {get_css(Selector.novel_cover)}, attr="src")
        ctx.novel.details = str(soup.select_one({get_css(Selector.novel_details)})).strip()

        # Parse authors
        author = Author({get_css(Selector.novel_author)}, AuthorType.AUTHOR)
        ctx.authors.add(author)

        # TODO: Parse volumes and chapters
        # volume = ctx.add_volume(serial)
        # chapter = ctx.add_chapter(serial, volume)

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        soup = self.get_sync(chapter.body_url).soup
        body = soup.select({get_css(Selector.chapter_content)})
        body = [TextUtils.sanitize_text(x.text) for x in body if x]
        chapter.body = '\\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])

'''

        src_folder = ModuleUtils.get_path(sources)
        src_file = os.path.join(src_folder, self.scraper_path)
        with open(src_file, 'w', encoding='utf8') as fp:
            fp.write(code)

        return 'Generated: ' + click.style(src_file, fg='blue', underline=True)
