# -*- coding: utf-8 -*-

from typing import List


class BinderConfig:
    def __init__(self, name: str, depends_on: List[str] = None):
        self.name: str = name
        self.requires: List[str] = depends_on or []
