# -*- coding: utf-8 -*-

from lncrawl.app import (Author, AuthorType, Chapter, Context, Language,
                         SoupUtils, TextUtils, UrlUtils, Volume)
from lncrawl.app.scraper import Scraper


class WwwNovelhallCom(Scraper):
    version: int = 1
    base_urls = ['https://www.novelhall.com/']

    def login(self, ctx: Context) -> bool:
        pass

    def fetch_info(self, ctx: Context) -> None:
        soup = self.get_sync(ctx.toc_url).soup

        ctx.language = Language.ENGLISH

        # Parse novel
        ctx.novel.name = SoupUtils.select_value(
            soup, "#main div.container div.book-main.inner.mt30 div.book-info h1")
        ctx.novel.name = TextUtils.ascii_only(ctx.novel.name)

        ctx.novel.cover_url = SoupUtils.select_value(
            soup, "#main div.container div.book-main.inner.mt30 div.book-img.hidden-xs img", attr="src")
        ctx.novel.details = str(soup.select_one(
            "#main div.container div.book-main.inner.mt30 div.book-info div.intro span.js-close-wrap")).strip()

        # Parse authors
        author = Author(
            "#main div.container div.book-main.inner.mt30 div.book-info div.total.booktag span.blue", AuthorType.AUTHOR)
        ctx.authors.add(author)

        # TODO: Parse volumes and chapters
        # volume = ctx.add_volume(serial)
        # chapter = ctx.add_chapter(serial, volume)

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        soup = self.get_sync(chapter.body_url).soup
        body = soup.select("")
        body = [TextUtils.sanitize_text(x.text) for x in body if x]
        chapter.body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])
