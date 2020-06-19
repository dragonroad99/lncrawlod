# -*- coding: utf-8 -*-

from enum import Enum, auto
from .context import Context


class EventType(Enum):
    PRE_INIT = auto()
    POST_INIT = auto()
    PRE_FETCH_INFO = auto()
    POST_FETCH_INFO = auto()
    PRE_FETCH_CHAPTER = auto()
    POST_FETCH_CHAPTER = auto()
    ADD_VOLUME = auto()
    ADD_CHAPTER = auto()
    PRE_INPUT = auto()
    POST_INPUT = auto()


class Event:
    def __init__(self, ctx: Context, evt_type: EventType, data: Any = None):
        self.ctx = ctx
        self.type = evt_type
        self.data = data
