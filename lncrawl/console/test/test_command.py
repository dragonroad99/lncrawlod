# -*- coding: utf-8 -*-

from cleo import Command


class TestCommand(Command):
    """
    Run live tests

    test
    """

    def handle(self):
        try:
            from lncrawl.app import CONFIG
            self.line(str(CONFIG.get('browser/parser/cloudscraper')))
            self.line(str(CONFIG.get('logging/version')))
            self.line(str(CONFIG.get('logging/loggers/level')))
        finally:
            self.line('')

        try:
            from lncrawl.app import (Author, AuthorType, Chapter, Language,
                                     Novel, Volume)
            self.line(str(Language.ENGLISH))
            author = Author('Sudipto Chandra', AuthorType.AUTHOR)
            self.line(str(author))
            novel = Novel('http://www.google.com')
            self.line(str(novel))
            volume = Volume(novel, 2)
            self.line(str(volume))
            chapter = Chapter(volume, 10, 'body_url')
            self.line(str(chapter))
        finally:
            self.line('')

        # try:
        #     from lncrawl.app.browser import Browser
        #     b = Browser()
        #     duck = b.get('https://duckduckgo.com/')
        #     print(duck)
        #     print(duck.soup.select_one('link[rel="canonical"]')['href'])
        #     print(duck.soup.find('meta', {'name': 'viewport'})['content'])
        # finally:
        #     print()

        # try:
        #     from lncrawl.app.browser import AsyncBrowser
        #     ab = AsyncBrowser()
        #     novel = ab.get('https://api.duckduckgo.com/?q=novel&format=json')
        #     anything = ab.get('https://api.duckduckgo.com/?q=anything&format=json')
        #     print(novel.result().json['AbstractURL'])
        #     print(anything.result().json['AbstractURL'])
        # finally:
        #     print()

        try:
            from lncrawl.app import binder
            self.line(str(binder.binder_list()))
            self.line(str(list(binder.binder_list())[0].config.name))
            self.line(str(binder.get_binder('json')))
        finally:
            self.line('')

        try:
            from lncrawl.app import scraper
            self.line(str(scraper.scraper_list()))
            self.line(str(list(scraper.scraper_list())[0].base_urls))
            self.line(str(scraper.get_scraper_by_url('https://lnmtl.com/novel/dragon-of-the-root')))
            self.line(str(scraper.get_scraper_by_name('lnmtl')))
        finally:
            self.line('')

        try:
            from lncrawl.app import Context
            context = Context('https://lnmtl.com/novel/dragon-of-the-root')
            context.login_id = 'dipu@gmail.com'
            context.login_password = 'password'
            self.line(str(context))

            # context.login()
            context.fetch_info()
            self.line(str(context.novel))
            self.line(str([str(x) for x in context.volumes]))
            self.line(str([str(x) for x in context.chapters]))
            self.line('')

            chap = context.get_chapter(1)
            if chap is not None:
                context.fetch_chapter_by_serial(1)
                self.line(chap.body)

            context.bind_books()
        finally:
            self.line('')
