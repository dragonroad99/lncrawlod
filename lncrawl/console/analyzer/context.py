# -*- coding: utf-8 -*-

import inspect
import os
import re
from urllib.parse import urlparse

import click
import questionary
from bs4 import BeautifulSoup, Tag
from slugify import slugify

from lncrawl import sources
from lncrawl.app import ModuleUtils, SoupUtils
from lncrawl.app.browser import Browser, BrowserResponse
from .models import Selector


class Command:
    def __init__(self, method):
        self.method = method
        self.name = method.__name__


class AnalyzerContext:
    def __init__(self):
        self.browser = Browser()
        self.url: str = None
        self.response: BrowserResponse = None
        self.soup: BeautifulSoup = None
        self.scraper_url: str = None
        self.scraper_name: str = None
        self.scraper_path: str = None
        self._selectors = dict()

    def _get_globals(self) -> dict:
        return dict(inspect.getmembers(self))

    def _eval(self, code: str):
        return eval(code, self._get_globals())

    def _get_command(self, name: str):
        name = name.strip().lower()
        if name[0] == '_':
            return None
        method = getattr(self, name, '')
        if not inspect.ismethod(method):
            return None
        return method

    def _process_command(self, method):
        if not inspect.ismethod(method):
            return
        kwargs = {}
        for key, val in inspect.signature(method).parameters.items():
            if val.annotation == bool:
                kwargs[key] = questionary.confirm(key).ask()
            else:
                kwargs[key] = questionary.text(key).ask()
            if val.annotation == int:
                kwargs[key] = int(kwargs[key])
            elif val.annotation == float:
                kwargs[key] = float(kwargs[key])
        return method(**kwargs)

    def _locate(self, text: str, attr: str = None) -> dict:
        '''Find css selector by text or attribute value.

        To find by attribute value, pass the attribute name,
        or keep it empty to find by text'''
        if not attr:  # find by text
            return {
                self.get_selector(node.parent): str(node)
                for node in self.soup.find_all(
                    string=re.compile(text, flags=re.IGNORECASE),
                    recursive=True
                )
            }
        else:  # find by attribute value
            return {
                self.get_selector(node): str(node)
                for node in self.soup.find_all(
                    attrs={attr: text},
                    recursive=True
                )
            }

    ###########################################################################
    #                           Imported Methods                              #
    ###########################################################################

    from .help import help
    from .generator import generate

    ###########################################################################
    #                              Regular Methods                            #
    ###########################################################################

    def save(self, name: str, selector: str, attribute: str = 'text') -> None:
        '''Set a selector for generator'''
        self._selectors[name] = [selector, attribute]

    def view(self):
        '''Check list of all available selector names'''
        message = ''
        for selector_name in Selector.values():
            message += click.style(selector_name, fg='green')
            message += ' = '
            arr = self._selectors.get(selector_name, [])
            css = arr[0] if len(arr) >= 1 else None
            attr = arr[1] if len(arr) >= 2 else 'text'
            message += click.style(selector_name, fg='cyan')
            message += '[%s]' % attr
            message += '\n'
            if not css:
                continue
            val = SoupUtils.select_value(self.soup, css, attr)
            if len(val) > 200:
                val = '%s... (%d more lines)\n' % (val[:180], len(val) - 180)
            message += click.style(val, fg='white', dim=True)
            message += '\n'
        return message

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

        self.scraper_path = os.path.join(
            ModuleUtils.get_path(sources),
            'generated',
            slugify(host, max_length=30) + '.py'
        )
        click.echo(f'scraper_path = {self.scraper_path}')

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

    def locate_text(self, text: str) -> str:
        selectors = self._locate(text)
        if not selectors:
            return 'No matching selectors.'
        result = f'Found {len(selectors)} matching selector(s):\n'
        result += '\n'.join([
            ' > '.join([
                click.style(k, fg='green', bold=True),
                click.style(v, fg='white', dim=True),
            ]) for k, v in selectors.items()
        ])
        return result

    def locate_attr(self, attr: str, value: str) -> str:
        selectors = self._locate(value, attr)
        if not selectors:
            return 'No matching selectors.'
        result = f'Found {len(selectors)} matching selector(s):\n'
        result += '\n'.join([
            ' > '.join([
                click.style(k, fg='green', bold=True),
                click.style(v, fg='white', dim=True),
            ]) for k, v in selectors.items()
        ])
        return result

    def locate(self):
        '''Locate a selector and save it'''
        by_text = questionary.select('What do you want to search by?', [
            'by text',
            'by attribute value'
        ]).unsafe_ask() == 'by text'

        attr = None
        selectors = {}
        if by_text:
            text = questionary.text('text').unsafe_ask()
            selectors = self._locate(text)
        else:
            attr = questionary.text('attribute name').unsafe_ask()
            value = questionary.text('attribute value').unsafe_ask()
            selectors = self._locate(value, attr)

        if not selectors:
            return 'No matching selectors.'

        keys = list(selectors.keys())
        css_value = keys[0]
        if len(selectors) > 1:
            value = questionary.select('Select which to save', [
                '%d. %s\n      %s' % (index, k, v)
                for index, (k, v) in enumerate(selectors.items())
            ]).unsafe_ask()
            css_value = keys[int(value.split('.')[0])]
        else:
            click.echo('Found 1 selector: ', nl=False)
            click.eecho(click.style(css_value, fg='yellow', bold=True))

        selector_name = questionary.select('Select where to save', [
            '%s (%s)' % (s, '::'.join(self._selectors.get(s, ['empty'])))
            for s in Selector.values()
        ]).unsafe_ask().split(' ')[0]

        self.save(selector_name, css_value, attr)

    def modify(self):
        selector_name = questionary.select('Select where to save', [
            '%s (%s)' % (s, '::'.join(self._selectors.get(s, ['empty'])))
            for s in Selector.values()
        ]).unsafe_ask().split(' ')[0]

        arr = self._selectors.get(selector_name, [])
        css = arr[0] if len(arr) >= 1 else ''
        attr = arr[1] if len(arr) >= 2 else 'text'

        css = questionary.text('selector', default=css).unsafe_ask()
        attr = questionary.text('attribute name', default=attr).unsafe_ask()
        self._selectors[selector_name] = [css, attr]
