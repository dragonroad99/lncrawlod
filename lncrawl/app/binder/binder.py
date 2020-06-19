# -*- coding: utf-8 -*-

import logging
import os
import shutil
from abc import ABC, abstractmethod

from ..context.context import Context
from .config import BinderConfig


class Binder(ABC):
    def __init__(self, name: str):
        self.config = BinderConfig(name)
        self.log = logging.getLogger(name)

    @abstractmethod
    def process(self, ctx: Context):
        raise NotImplementedError()

    def make_output_path(self, ctx: Context) -> str:
        if not hasattr(self, '_out_dir'):
            out_dir: str = os.path.join(ctx.output_path, self.config.name)
            if os.path.exists(out_dir) and not ctx.keep_old_path:
                shutil.rmtree(out_dir)
            os.makedirs(out_dir, exist_ok=True)
            self._out_dir: str = out_dir
        return self._out_dir
