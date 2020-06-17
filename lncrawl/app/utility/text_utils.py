# -*- coding: utf-8 -*-

import re

re_ascii_only = re.compile('[^\u0000-\u00FF]', re.UNICODE)


class TextUtils:

    @staticmethod
    def ascii_only(text: str) -> str:
        '''Removes all non-ASCII characters'''
        return re_ascii_only.sub('', text or '')

    @staticmethod
    def sanitize_text(text: str) -> str:
        '''Remove or replace bad characters from text'''
        text = text.replace(u'\u00ad', '')
        text = re.sub(r'\u201e[, ]*', '&ldquo;', text)
        text = re.sub(r'\u201d[, ]*', '&rdquo;', text)
        text = re.sub(r'[ ]*,[ ]+', ', ', text)
        return text.strip()
