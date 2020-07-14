# -*- coding: utf-8 -*-

from typing import Dict

from bs4 import Tag  # type: ignore


class SoupUtils:

    @staticmethod
    def get_value(node: Tag, attr: str = 'text') -> str:
        ''''Returns the value an attribute.

        :param node: The node in which to search
        :param attr: The attribute name (default: text)
        '''
        if not node:
            return ''
        if hasattr(node, 'has_attr') and node.has_attr(attr):
            return str(node.get(attr) or '')
        if hasattr(node, attr):
            return str(getattr(node, attr) or '')
        return ''

    @staticmethod
    def select_value(node: Tag,
                     selector: str = None,
                     attr: str = 'text') -> str:
        '''Select first matching tag by selector.

        :param node: The node in which to search
        :param selector: A css selector
        :param value_of: The attribute to select (default: text)
        '''
        tag = node.select_one(selector or '')
        text = SoupUtils.get_value(tag, attr)
        return text.strip()

    @staticmethod
    def find_value(node: Tag,
                   name: str = None,
                   attrs: Dict[str, str] = {},
                   recursive: bool = True,
                   text: str = None,
                   value_of: str = 'text') -> str:
        '''Find matching tag by provided params. See node

        :param node: The node in which to search
        :param value_of: The attribute to select (default: text)
        :param name, attrs, recursive, text: Same as node.find() method
        '''
        tag = node.find(name, attrs, recursive, text)
        text = SoupUtils.get_value(tag, value_of)
        return text.strip()
