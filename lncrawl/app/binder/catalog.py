# -*- coding: utf-8 -*-
"""
Auto imports all binder from the lncrawl.binders
"""

from typing import Dict, FrozenSet

from ... import binders
from ..utility import ModuleUtils
from .binder import Binder

# This list will be auto-generated
_binders: Dict[str, Binder] = dict()


def binder_names() -> FrozenSet[str]:
    return frozenset(_binders.keys())


def binder_list() -> FrozenSet[Binder]:
    return frozenset(_binders.values())


def get_binder(binder_name: str) -> Binder:
    return _binders[binder_name]


# To auto-import all submodules
_modules = ModuleUtils.find_modules(binders, base=Binder)
for name, binder in _modules.items():
    instance = binder(name)
    _binders[name] = instance
