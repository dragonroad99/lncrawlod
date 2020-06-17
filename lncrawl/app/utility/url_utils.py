# -*- coding: utf-8 -*-

from typing import Dict, List, Union, Any
from urllib.parse import (ParseResult, parse_qs, quote, urlencode, urlparse,
                          urlunparse)


QueryType = Dict[str, Union[str, List[Any]]]


class UrlUtils:
    @staticmethod
    def join(base: str, url: str):
        '''Make provided url absolute to the base url'''
        base_parsed = urlparse(base)
        parse_result = urlparse(url)
        scheme, netloc, path, params, query, fragment = parse_result
        if not scheme:
            scheme = base_parsed.scheme
            if not netloc:
                netloc = base_parsed.netloc
                if not params:
                    params = base_parsed.params
                if not path:
                    path = base_parsed.path
                elif not path.startswith('/'):
                    path = base_parsed.path + '/' + path

        final_result = ParseResult(scheme, netloc, path, params, query, fragment)
        return urlunparse(final_result)

    @staticmethod
    def format(url: str,
               path: Union[str, List[str]] = None,
               query: Union[str, QueryType] = None,
               fragment: str = None) -> str:
        '''Add the extra sauce to the URL'''
        parse_result = urlparse(url)
        _scheme, _netloc, _path, _params, _query, _fragment = parse_result

        if query:
            query_dict = {}
            if isinstance(query, str):
                query_dict.update(parse_qs(query, keep_blank_values=False))
            else:
                for key, val in query.items():
                    query_dict.setdefault(key, [])
                    query_dict[key] = val if isinstance(val, list) else [str(val)]

            parsed_query = parse_qs(_query, keep_blank_values=True)
            for key, val in query_dict.items():
                parsed_query.setdefault(key, [])
                parsed_query[key] += val
            _query = urlencode(parsed_query, doseq=True)

        if path:
            if isinstance(path, str):
                path = [path]
            _path = '/'.join(path)

        if fragment:
            _fragment = quote(fragment)

        final_result = ParseResult(_scheme, _netloc, _path, _params, _query, _fragment)
        return urlunparse(final_result)
