# -*- coding: utf-8 -*-

import time

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

    click.echo(ctx.generate())
    click.echo()
    while True:
        try:
            time.sleep(0.05)
            process_input(ctx)
        except EOFError:
            break
        except (KeyboardInterrupt, Exception):
            pass

    click.echo(ctx.generate())
