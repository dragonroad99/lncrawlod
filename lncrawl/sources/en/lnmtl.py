# -*- coding: utf-8 -*-

import js2py  # type: ignore

from lncrawl.app.context import Context
from lncrawl.app.models import Author, AuthorType, Chapter, Language, Volume
from lncrawl.app.scraper import Scraper
from lncrawl.app.utility import SoupUtils, TextUtils, UrlUtils

LOGIN_URL = 'https://lnmtl.com/auth/login'
LOGOUT_URL = 'https://lnmtl.com/auth/logout'


class LNMTLScraper(Scraper):
    version: int = 1
    base_urls = ['https://lnmtl.com/']

    def login(self, ctx: Context) -> bool:
        soup = self.get_sync(LOGIN_URL).soup
        if soup.find('a', {'href': LOGOUT_URL}):
            return True

        token = SoupUtils.select_value(soup, 'form input[name="_token"]', 'value')
        self.log.debug('Login token: %s', token)
        response = self.post_sync(LOGIN_URL, body={
            '_token': token,
            'email': ctx.login_id,
            'password': ctx.login_password,
        })

        soup = response.soup
        if not soup.find('a', {'href': LOGOUT_URL}):
            error = SoupUtils.select_value(soup, '.has-error .help-block')
            raise Exception(error or 'Failed to login')
        return True

    def fetch_info(self, ctx: Context) -> None:
        soup = self.get_sync(ctx.toc_url).soup

        ctx.language = Language.ENGLISH

        # Parse novel
        ctx.novel.name = SoupUtils.select_value(soup, '.novel .media .novel-name')
        ctx.novel.name = TextUtils.ascii_only(ctx.novel.name)

        ctx.novel.cover_url = SoupUtils.select_value(soup, '.novel .media img', 'src')
        ctx.novel.details = str(soup.select_one('.novel .media .description')).strip()

        # Find authors
        for dl in soup.select('.panel-default .panel-body dl'):
            key = dl.find('dt').text
            if key == 'Authors':
                value = TextUtils.ascii_only(dl.find('dd').text)
                author = Author(value, AuthorType.AUTHOR)
                ctx.authors.add(author)

        # Parse volumes
        script = soup.find(name='main').find_next_sibling(name='script').string
        data = js2py.eval_js("window = {}; lnmtl = {};" + script + "; lnmtl;").to_dict()

        ctx.extra['futures'] = []
        for i, item in enumerate(data['volumes']):
            serial = int(item.get('number', i + 1))
            vol = ctx.add_volume(serial)
            vol.extra = item
            vol.name = TextUtils.ascii_only(item.get('title', ''))

            f = self.submit_task(self.fetch_chapter_list, ctx, data['route'], vol)
            ctx.extra['futures'].append(f)

        # Wait for all chapters
        while ctx.extra['futures']:
            ctx.extra['futures'].pop(0).result()
        del ctx.extra['futures']

    def fetch_chapter_list(self, ctx: Context, url: str, volume: Volume, page=1):
        url = UrlUtils.format(url, query={
            'page': page,
            'volumeId': volume.get_extra('id')
        })
        result = self.get_sync(url).json

        for i, item in enumerate(result['data']):
            serial = volume.serial * 100 + i + 1
            serial = int(item.get('number', serial))
            chap = ctx.add_chapter(serial, volume)
            chap.extra = item
            chap.body_url = item.get('site_url', '')
            chap.name = TextUtils.ascii_only(item.get('title', ''))

        if page < result.get('last_page', page):
            f = self.submit_task(self.fetch_chapter_list, ctx, url, volume, page + 1)
            ctx.extra['futures'].append(f)

    def fetch_chapter(self, ctx: Context, chapter: Chapter) -> None:
        soup = self.get_sync(chapter.body_url).soup
        body = soup.select('.chapter-body .translated')
        body = [TextUtils.sanitize_text(x.text) for x in body if x]
        chapter.body = '\n'.join(['<p>%s</p>' % (x) for x in body if len(x)])
