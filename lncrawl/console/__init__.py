# -*- coding: utf-8 -*-

import click

from .. import __version__

from .app import app
from .analyzer import analyze

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.pass_context
@click.option('-v', '--version', is_flag=True, help='Show current version and exit.')
def main(ctx, version):
    """Download and generate e-books from online sources."""
    if version:
        click.echo('Lightnovel Crawler %s' % __version__)
        ctx.exit()


main.add_command(app)
main.add_command(analyze)
