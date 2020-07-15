# -*- coding: utf-8 -*-

from lncrawl.app import (Author, AuthorType, Chapter, Context, Language,
                         SoupUtils, TextUtils, UrlUtils, Volume)
from lncrawl.app.scraper import Scraper


class WuxiaworldWorld(Scraper):
    version: int = 1
    base_urls = ['https://wuxiaworld.world/']

    def login(self, ctx: Context) -> bool:
        pass

    def fetch_info(self, ctx: Context) -> None:
        soup = self.get_sync(ctx.toc_url).soup

        ctx.language = Language.ENGLISH

        # Parse novel
        ctx.novel.name = SoupUtils.select_value(
            soup, "div.content_left div.manga_info div.manga_info_right div.manga_name h1", attr="text")
        ctx.novel.name = TextUtils.ascii_only(ctx.novel.name)

        ctx.novel.cover_url = SoupUtils.select_value(
            soup, "div.content_left div.manga_info div.manga_info_left div.manga_info_img img.img-responsive", attr="src")
        # ctx.novel.details = str(soup.select_one("")).strip()

        # Parse authors
        _author = SoupUtils.select_value(
            soup, "div.manga_info_right div.manga_des ul li a", attr="text")
        _author = TextUtils.ascii_only(_author)
        ctx.authors.add(Author(_author, AuthorType.AUTHOR))

        # Parse volumes and chapters
        for serial, a in enumerate(soup.select("#content li div.chapter_number a")):
            volume = ctx.add_volume(1 + serial // 100)
            chapter = ctx.add_chapter(serial, volume)
            chapter.body_url = a['href']
            chapter.name = TextUtils.sanitize_text(a.text)

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        soup = self.get_sync(chapter.body_url).soup
        body = soup.select("div#content")
        body = [TextUtils.sanitize_text(x.text) for x in body if x]
        chapter.body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])
