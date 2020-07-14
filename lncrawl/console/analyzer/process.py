# -*- coding: utf-8 -*-

import traceback

import click
import questionary

from .context import AnalyzerContext


def process_input(ctx: AnalyzerContext):
    code = questionary.text('', qmark='>>>').unsafe_ask()

    if not code:
        return
    elif code == 'exit':
        raise EOFError
    elif code == 'clear':
        click.clear()
        return

    try:
        command = code.strip().split(' ')[0]
        if command in ctx._get_commands():
            result = getattr(ctx, command)()
        else:
            result = eval(code, ctx._get_globals())

        result = str(result)
        if len(result) < 5000:
            click.echo(result, color=True)
        else:
            click.echo_via_pager(result, color=True)
    except Exception:
        err = traceback.format_exc(chain=False)
        click.echo(click.style(err, fg='red', dim=True))
