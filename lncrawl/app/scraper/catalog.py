# -*- coding: utf-8 -*-
"""
Auto imports all crawlers from the lncrawl.sources
"""
import logging
import re
from typing import FrozenSet, Union, Dict
from urllib.parse import urlparse

from ... import sources
from ..utility import ModuleUtils
from .scraper import Scraper

logger = logging.getLogger(__name__)

# This list will be auto-generated
_scrapers: Dict[str, Scraper] = dict()


def scraper_list() -> FrozenSet[Scraper]:
    return frozenset(_scrapers.values())


def is_rejected_source(url: str) -> bool:
    host = urlparse(url).netloc
    if host in sources.rejected_sources:
        return True
    return False


def raise_if_rejected(url: str) -> None:
    host = urlparse(url).netloc
    if host in sources.rejected_sources:
        raise Exception(sources.rejected_sources[host])


def get_scraper_by_url(url: str) -> Union[Scraper, None]:
    raise_if_rejected(url)
    parsed_url = urlparse(url)
    return _scrapers[parsed_url.netloc]


def get_scraper_by_name(name: str) -> Union[Scraper, None]:
    for scraper in _scrapers.values():
        if getattr(scraper, 'name', '') == name:
            return scraper
    return None


# To auto-import all submodules
re_url = re.compile(r'^^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.I)

logger.debug('Discovering sources...')
_modules = ModuleUtils.find_modules(sources, base=Scraper)
for name, scraper in _modules.items():
    base_urls = getattr(scraper, 'base_urls')
    if not isinstance(base_urls, list):
        raise Exception(name + ': `base_urls` should be a list of strings')

    new_base_urls = []
    for url in base_urls:
        url = url.strip().strip('/')
        if re_url.match(url):
            new_base_urls.append(url)

    if len(new_base_urls) == 0:
        raise Exception(name + ': `base_urls` should contain at least one valid url')

    if any(is_rejected_source(url) for url in new_base_urls):
        continue  # do not add rejected scraper

    instance = scraper(name)
    instance.base_urls = new_base_urls
    for url in new_base_urls:
        parsed_url = urlparse(url)
        key = parsed_url.netloc
        if key in _scrapers:
            other = _scrapers[key].name
            raise Exception(f'{name}: "{url}" is already being used by "{other}"')
        _scrapers[key] = instance
