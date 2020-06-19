# -*- coding: utf-8 -*-

__version__ = '3.0.0-alpha'


def main():
    from .app.arguments import get_args
    print(get_args())
