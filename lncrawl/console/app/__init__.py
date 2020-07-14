# -*- coding: utf-8 -*-

import click
import questionary


@click.command()
@click.option('-s', '--url', type=str, help="URL of novel's table of contents page")
def app(url):
    """Test features"""
    if not url:
        url = questionary.text('Please enter an URL:').ask()

    try:
        from lncrawl.app import Context
        context = Context(url)
        click.echo(context)

        # context.login()
        context.fetch_info()
        click.echo(context.novel)
        click.echo('%d volumes found' % len(context.volumes))
        click.echo('%d chapters found' % len(context.chapters))
        chap = context.get_chapter(1)
        if chap is not None:
            context.fetch_chapter_by_serial(1)
            click.echo('body length: %d' % len(chap.body))

        click.echo('')

        context.bind_books()
        click.echo('Output saved to: %s' % context.output_path)
    finally:
        click.echo('')

    # try:
    #     from lncrawl.app import CONFIG
    #     click.echo(str(CONFIG.get('browser/parser/cloudscraper')))
    #     click.echo(str(CONFIG.get('logging/version')))
    #     click.echo(str(CONFIG.get('logging/loggers/level')))
    # finally:
    #     click.echo('')

    # try:
    #     from lncrawl.app import Author, AuthorType, Chapter, Language, Novel, Volume
    #     click.echo(str(Language.ENGLISH))
    #     author = Author('Sudipto Chandra', AuthorType.AUTHOR)
    #     click.echo(str(author))
    #     novel = Novel('http://www.google.com')
    #     click.echo(str(novel))
    #     volume = Volume(novel, 2)
    #     click.echo(str(volume))
    #     chapter = Chapter(volume, 10, 'body_url')
    #     click.echo(str(chapter))
    # finally:
    #     click.echo('')

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

    # try:
    #     from lncrawl.app import binder
    #     click.echo(str(binder.binder_list()))
    #     click.echo(str(list(binder.binder_list())[0].config.name))
    #     click.echo(str(binder.get_binder('json')))
    # finally:
    #     click.echo('')

    # try:
    #     from lncrawl.app import scraper
    #     click.echo(str(scraper.scraper_list()))
    #     click.echo(str(list(scraper.scraper_list())[0].base_urls))
    #     click.echo(str(scraper.get_scraper_by_url(
    #         'https://lnmtl.com/novel/dragon-of-the-root')))
    #     click.echo(str(scraper.get_scraper_by_name('lnmtl')))
    # finally:
    #     click.echo('')
