# -*- coding: utf-8 -*-

import json
import os

import click
from .models import Selector


def generate(self):
    '''Genrate source file with current selectors'''
    if os.path.exists(self.scraper_path):
        if not click.confirm('Replace existing file?'):
            return

    def get_selector(selector: Selector):
        arr = self._selectors.get(selector.name, [])
        css = json.dumps(arr[0] if len(arr) >= 1 else '')
        attr = json.dumps(arr[1] if len(arr) >= 2 else 'text')
        return (css, attr)

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
        ctx.novel.name = SoupUtils.select_value(soup, {'%s, attr=%s' % get_selector(Selector.novel_name)})
        ctx.novel.name = TextUtils.ascii_only(ctx.novel.name)

        ctx.novel.cover_url = SoupUtils.select_value(soup, {'%s, attr=%s' % get_selector(Selector.novel_cover)})
        ctx.novel.details = str(soup.select_one({get_selector(Selector.novel_details)[0]})).strip()

        # Parse authors
        _author = SoupUtils.select_value(soup, {'%s, attr=%s' % get_selector(Selector.novel_author)})
        _author = TextUtils.ascii_only(_author)
        ctx.authors.add(Author(_author, AuthorType.AUTHOR))

        # Parse volumes and chapters
        for serial, a in enumerate(soup.select({get_selector(Selector.chapter_list)[0]})):
            volume = ctx.add_volume(1 + serial // 100)
            chapter = ctx.add_chapter(serial, volume)
            chapter.body_url = a['href']
            chapter.name = TextUtils.sanitize_text(a.text)

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        soup = self.get_sync(chapter.body_url).soup
        body = soup.select({get_selector(Selector.chapter_content)[0]})
        body = [TextUtils.sanitize_text(x.text) for x in body if x]
        chapter.body = '\\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])

'''
    os.makedirs(os.path.dirname(self.scraper_path), exist_ok=True)
    with open(self.scraper_path, 'w', encoding='utf8') as fp:
        fp.write(code)
    return 'Generated: ' + click.style(self.scraper_path, fg='blue', underline=True)
