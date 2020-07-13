# -*- coding: utf-8 -*-

import click


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def analyze(count, name):
    """Autogenerate crawler by analyzing an url"""
    for x in range(count):
        click.echo('Hello %s!' % name)
