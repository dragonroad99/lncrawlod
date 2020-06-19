# -*- coding: utf-8 -*-

import os
import re
from glob import glob
from importlib import import_module
from types import ModuleType
from typing import Any, Dict

re_active_module_file = re.compile(r'^([^_.][^.]+).py[c]?$', re.IGNORECASE)


class ModuleUtils:

    @staticmethod
    def get_version() -> str:
        from lncrawl import __version__
        return __version__

    @staticmethod
    def find_modules(src: ModuleType, base: Any) -> Dict[str, Any]:
        src_dir = os.path.abspath(getattr(src, '__path__')[0])
        if os.sep != '/':
            src_dir = src_dir.replace(os.sep, '/')

        result: Dict[str, Any] = dict()
        for file_path in glob(src_dir + '/**/*.py', recursive=True):
            if not os.path.isfile(file_path):
                continue

            file_name = os.path.basename(file_path)
            if not re_active_module_file.match(file_name):
                continue

            rel_path = file_path[len(src_dir) + 1:-3]
            module_name = rel_path.replace(os.sep, '.')
            package_name = getattr(src, '__package__')
            module = import_module('.' + module_name, package_name)

            for key in dir(module):
                klass = getattr(module, key)
                if getattr(klass, '__base__', None) == base:
                    result[module_name] = klass

        return result
