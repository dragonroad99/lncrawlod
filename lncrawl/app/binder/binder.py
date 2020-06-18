# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import List

from ..context import Context

logging.basicConfig()


class Binder(ABC):
    requires: List[str] = []

    def __init__(self, name: str):
        self.name = name
        self.log = logging.getLogger(name)

    @abstractmethod
    def process(self, ctx: Context):
        raise NotImplementedError()
