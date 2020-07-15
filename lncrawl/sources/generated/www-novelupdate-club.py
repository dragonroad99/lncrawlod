# -*- coding: utf-8 -*-

from lncrawl.app import (Author, AuthorType, Chapter, Context, Language,
                         SoupUtils, TextUtils, UrlUtils, Volume)
from lncrawl.app.scraper import Scraper


class WwwNovelupdateClub(Scraper):
    version: int = 1
    base_urls = ['https://www.novelupdate.club/']

    def login(self, ctx: Context) -> bool:
        pass

    def fetch_info(self, ctx: Context) -> None:
        soup = self.get_sync(ctx.toc_url).soup

        ctx.language = Language.ENGLISH

        # Parse novel
        ctx.novel.name = SoupUtils.select_value(
            soup, "h1.widget-title", attr="text")
        ctx.novel.name = TextUtils.ascii_only(ctx.novel.name)

        ctx.novel.cover_url = SoupUtils.select_value(
            soup, "img.lazyload.img-fluid.p-0.mb-3", attr="data-src")
        ctx.novel.details = str(soup.select_one(
            "div[itemprop='description']")).strip()

        # Parse authors
        # _author = SoupUtils.select_value(soup, "", attr="text")
        # _author = TextUtils.ascii_only(_author)
        # ctx.authors.add(Author(_author, AuthorType.AUTHOR))

        # Parse volumes and chapters
        for serial, a in enumerate(reversed(soup.select("div.post div.row a.col-md-6"))):
            volume = ctx.add_volume(1 + serial // 100)
            chapter = ctx.add_chapter(serial, volume)
            chapter.body_url = a['href']
            chapter.name = TextUtils.sanitize_text(a.text)

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        soup = self.get_sync(chapter.body_url).soup
        body = soup.select("div.post.post-single p")
        body = [TextUtils.sanitize_text(x.text) for x in body if x]
        chapter.body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])
