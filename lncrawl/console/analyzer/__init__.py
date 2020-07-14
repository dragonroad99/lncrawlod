# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor

import click
import questionary

from .context import AnalyzerContext
from .process import process_input


@click.command()
@click.option('-s', '--url', type=str, help='URL to analyze.')
def analyze(url):
    """Autogenerate crawler by analyzing an url"""

    ctx = AnalyzerContext()
    try:
        click.clear()
        if not url:
            url = questionary.text('Please enter an URL:').ask()
        url = url.strip(' /')
        ctx.set_url(url)
    except Exception as e:
        click.echo(str(e), err=True)
        return

    executor = ThreadPoolExecutor(max_workers=1)

    while True:
        try:
            future = executor.submit(process_input, ctx)
            future.result()
        except EOFError:
            break
    executor.shutdown()

    # TODO: generate crawler using ctx
