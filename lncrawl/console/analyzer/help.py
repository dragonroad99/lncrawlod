# -*- coding: utf-8 -*-

import inspect

import click


def help(self) -> str:
    '''Shows this message'''
    methods = []
    variables = []
    for key, val in inspect.getmembers(self):
        val = getattr(self, key)
        styled_key = click.style(key, fg='green', bold=True)
        if inspect.isbuiltin(val) or key[0] == '_':
            continue
        if inspect.ismethod(val):
            args = str(inspect.signature(val))
            args = click.style(args, dim=True)
            docs = inspect.getdoc(val)
            docs = '\n- ' + str(docs) if docs else ''
            methods.append(f"{styled_key}{args}{docs}")
        else:
            type_name = type(val).__name__
            val = str(val)
            if len(val) > 160:
                val = '%s ...(%d more lines)' % (val[:150], len(val) - 150)
            variables.append(f"{styled_key}:{type_name} = {val}")

    message = ''

    message += click.style(('=' * 20) + '\n', fg='white', dim=True)
    message += click.style('Variables:\n', bold=True)
    message += click.style(('=' * 20) + '\n', fg='white', dim=True)
    message += '\n'.join(variables)

    message += '\n\n'

    message += click.style(('=' * 20) + '\n', fg='white', dim=True)
    message += click.style('Methods:\n', bold=True)
    message += click.style(('=' * 20) + '\n', fg='white', dim=True)
    message += '\n'.join(methods)

    return message
