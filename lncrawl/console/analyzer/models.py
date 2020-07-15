# -*- coding: utf-8 -*-

from enum import IntEnum, auto


class Selector(IntEnum):
    novel_name = auto()
    novel_author = auto()
    novel_cover = auto()
    novel_details = auto()
    chapter_content = auto()
    chapter_list = auto()

    @staticmethod
    def values():
        return [s.name for s in Selector]
