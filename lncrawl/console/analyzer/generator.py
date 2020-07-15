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

    def comment(selector: Selector):
        arr = self._selectors.get(selector.name, [])
        return '# ' if not (arr and arr[0]) else ''

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
        {comment(Selector.novel_name)}ctx.novel.name = SoupUtils.select_value(soup, {'%s, attr=%s' % get_selector(Selector.novel_name)})
        {comment(Selector.novel_name)}ctx.novel.name = TextUtils.ascii_only(ctx.novel.name)

        {comment(Selector.novel_cover)}ctx.novel.cover_url = SoupUtils.select_value(soup, {'%s, attr=%s' % get_selector(Selector.novel_cover)})
        {comment(Selector.novel_details)}ctx.novel.details = str(soup.select_one({get_selector(Selector.novel_details)[0]})).strip()

        # Parse authors
        {comment(Selector.novel_author)}_author = SoupUtils.select_value(soup, {'%s, attr=%s' % get_selector(Selector.novel_author)})
        {comment(Selector.novel_author)}_author = TextUtils.ascii_only(_author)
        {comment(Selector.novel_author)}ctx.authors.add(Author(_author, AuthorType.AUTHOR))

        # Parse volumes and chapters
        {comment(Selector.chapter_list)}for serial, a in enumerate(soup.select({get_selector(Selector.chapter_list)[0]})):
        {comment(Selector.chapter_list)}    volume = ctx.add_volume(1 + serial // 100)
        {comment(Selector.chapter_list)}    chapter = ctx.add_chapter(serial, volume)
        {comment(Selector.chapter_list)}    chapter.body_url = a['href']
        {comment(Selector.chapter_list)}    chapter.name = TextUtils.sanitize_text(a.text)

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        soup = self.get_sync(chapter.body_url).soup
        {comment(Selector.chapter_content)}body = soup.select({get_selector(Selector.chapter_content)[0]})
        {comment(Selector.chapter_content)}body = [TextUtils.sanitize_text(x.text) for x in body if x]
        {comment(Selector.chapter_content)}chapter.body = '\\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])

'''
    os.makedirs(os.path.dirname(self.scraper_path), exist_ok=True)
    with open(self.scraper_path, 'w', encoding='utf8') as fp:
        fp.write(code)
    return 'Generated: ' + click.style(self.scraper_path, fg='blue', underline=True)
