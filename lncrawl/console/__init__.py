# -*- coding: utf-8 -*-

import sys

from cleo import Application

from .. import __version__
from .test import TestCommand

application = Application("lightnovel-crawler", __version__)
application.add(TestCommand())


def main() -> None:
    sys.exit(application.run())
