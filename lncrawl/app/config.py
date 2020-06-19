# -*- coding: utf-8 -*-

import atexit
import logging
import os
from typing import Any, Dict

import yaml
from atomicwrites import atomic_write

from .utility import DictUtils, PathType

_USER_HOME = os.path.expanduser('~')
_USER_DOCUMENTS = os.path.join(_USER_HOME, 'Documents')
_CURRENT_FOLDER = os.path.abspath(os.curdir)


class _Config:
    # Define configurations here
    __dict__: Dict[str, Any] = {
        'browser': {
            'parser': 'html5lib',
            'stream_chunk_size': 50 * 1024,  # in bytes
            'cloudscraper': {
                # Docs: https://github.com/VeNoMouS/cloudscraper
                'debug': False,
                'allow_brotli': False,
                'browser': {
                    'mobile': False
                },
                'delay': None,
                'interpreter': 'native',
                'recaptcha': None,
            },
        },
        'concurrency': {
            'max_connections': 1000,
            'max_workers': 10,
            'per_host': {
                'max_connections': 10,
                'semaphore_timeout': 5 * 60,  # seconds
            }
        },
        'sources': {
            # override source specific config here
            'en.lnmtl': {
                'concurrency': {
                    'max_workers': 2
                }
            }
        },
        'logging': {
            #
            # Configure logging
            # Docs: https://docs.python.org/3.5/library/logging.config.html#configuration-dictionary-schema
            # Example: https://stackoverflow.com/a/7507842/1583052
            #
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'console': {
                    'format': '%(asctime)s %(levelname)-8s %(message)s',
                    'datefmt': '%H:%M:%S',
                },
                'file': {
                    'format': '%(asctime)s [%(process)d] %(levelname)s\n@%(name)s: %(message)s\n',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
            },
            'handlers': {
                'console': {
                    'formatter': 'console',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',  # default is stderr
                },
                'file': {
                    'formatter': 'file',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'lncrawl.log',
                    'maxBytes': 1024 * 1024,  # 1 MB
                    'backupCount': 3,
                },
            },
            'loggers': {
                '': {  # root logger
                    'handlers': ['console'],
                    'level': logging.getLevelName(logging.INFO),
                },
            },
        },
    }

    #######################################################
    #                      INTERNALS                      #
    #######################################################

    _opened_file = None

    _config_files = [
        os.path.join(_CURRENT_FOLDER, 'Lightnovels', 'config.yaml'),
        os.path.join(_USER_DOCUMENTS, 'Lightnovels', 'config.yaml'),
    ]

    def __init__(self):
        self._load()

    def _load(self) -> None:
        try:
            for filepath in self._config_files:
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    self._opened_file = filepath
                    with open(self._opened_file, encoding='utf-8') as fp:
                        data = yaml.safe_load(fp)
                        DictUtils.merge(self.__dict__, data)
                        logging.info(f'Load config from {self._opened_file}')
                        break  # exit after first success
        except Exception:
            logging.exception('Failed to load config')
        finally:
            atexit.register(self._save)  # save at exit

    def _save(self) -> None:
        if not self._opened_file:
            for filepath in self._config_files:
                try:
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    self._opened_file = filepath
                    break  # exit after first success
                except (OSError, IOError):
                    pass
        try:
            if not self._opened_file:
                raise FileNotFoundError()
            with atomic_write(self._opened_file, overwrite=True) as fp:
                yaml.safe_dump(self.__dict__, fp, allow_unicode=True)
                logging.info(f'Saved config to {self._opened_file}')
        except Exception:
            logging.exception('Failed to save config')

    #######################################################
    #                   PUBLIC METHODS                    #
    #######################################################

    @property
    def workdir(self) -> str:
        if not self._opened_file:
            raise FileNotFoundError()
        return os.path.dirname(self._opened_file)

    def get(self, path: PathType, default: Any = None) -> Any:
        return DictUtils.get_value(self.__dict__, path, default)

    def put(self, path: PathType, value: Any) -> None:
        DictUtils.put_value(self.__dict__, path, value)

    def scraper(self, scraper_name: str, path: PathType, fallback: Any = None) -> Any:
        '''Returns config specific to a source'''
        default = self.get(path)
        scraper = self.get(['sources', scraper_name])
        scraper = DictUtils.get_value(scraper, path)
        if scraper is None:
            return default
        if isinstance(scraper, dict) and isinstance(default, dict):
            return DictUtils.merge({}, default, scraper)
        return scraper


# Create an instance config for quick access
CONFIG = _Config()
