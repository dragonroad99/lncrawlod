# -*- coding: utf-8 -*-
"""
Crawler application
"""
import logging
import re
from abc import abstractmethod
from concurrent import futures
from urllib.parse import urlparse, urljoin

import cloudscraper
from requests import Session
from bs4 import BeautifulSoup, Comment
from requests.adapters import Response

logger = logging.getLogger(__name__)

_default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'


class Crawler:
    '''Blueprint for creating new crawlers'''

    def __init__(self):
        self._destroyed = False
        self.executor = futures.ThreadPoolExecutor(max_workers=4)

        # Initialize cloudscrapper
        try:
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'platform': 'linux',
                    'mobile': False
                }
            )
        except Exception as err:
            logger.exception('Failed to initialize cloudscraper')
            self.scraper = Session()
        # end try

        # Must resolve these fields inside `read_novel_info`
        self.novel_title = 'N/A'
        self.novel_author = 'N/A'
        self.novel_cover = None
        self.is_rtl = False

        # Each item must contain these keys:
        # `id` - 1 based index of the volume
        # `title` - the volume title (can be ignored)
        self.volumes = []

        # Each item must contain these keys:
        # `id` - 1 based index of the chapter
        # `title` - the title name
        # `volume` - the volume id of this chapter
        # `volume_title` - the volume title (can be ignored)
        # `url` - the link where to download the chapter
        self.chapters = []

        # Other stuffs - not necessary to resolve from crawler instance.
        self.home_url = ''
        self.novel_url = ''
        self.last_visited_url = None
    # end def

    def destroy(self):
        self._destroyed = True
        self.volumes.clear()
        self.chapters.clear()
        self.scraper.close()
        self.executor.shutdown(False)
    # end def

    # ------------------------------------------------------------------------- #
    # Implement these methods
    # ------------------------------------------------------------------------- #

    @abstractmethod
    def initialize(self):
        pass
    # end def

    @abstractmethod
    def login(self, email, password):
        pass
    # end def

    @abstractmethod
    def logout(self):
        pass
    # end def

    @abstractmethod
    def search_novel(self, query):
        '''Gets a list of results matching the given query'''
        pass
    # end def

    @abstractmethod
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        pass
    # end def

    @abstractmethod
    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        pass
    # end def

    def get_chapter_index_of(self, url):
        '''Return the index of chapter by given url or 0'''
        url = (url or '').strip().strip('/')
        for chapter in self.chapters:
            if chapter['url'] == url:
                return chapter['id']
            # end if
        # end for
        return 0
    # end def

    # ------------------------------------------------------------------------- #
    # Helper methods to be used
    # ------------------------------------------------------------------------- #
    @property
    def headers(self):
        return self.scraper.headers.copy()
    # end def

    def set_header(self, key: str, value: str):
        self.scraper.headers[key.lower()] = value
    # end def

    @property
    def cookies(self):
        return {x.name: x.value for x in self.scraper.cookies}
    # end def

    def absolute_url(self, url, page_url=None):
        url = (url or '').strip()
        if not page_url:
            page_url = self.last_visited_url
        # end if
        if not url or len(url) == 0:
            return None
        elif url.startswith('//'):
            return self.home_url.split(':')[0] + ':' + url
        elif url.find('//') >= 0:
            return url
        elif url.startswith('/'):
            return self.home_url + url
        elif page_url:
            return page_url.strip('/') + '/' + url
        else:
            return self.home_url + url
        # end if
    # end def

    def is_relative_url(self, url):
        page = urlparse(self.novel_url)
        url = urlparse(url)
        return (page.hostname == url.hostname
                and url.path.startswith(page.path))
    # end def

    def get_response(self, url, **kargs):
        if self._destroyed:
            return None

        kargs = kargs or dict()
        #kargs.setdefault('verify', False)
        #kargs.setdefault('allow_redirects', True)
        kargs.setdefault('timeout', 150)  # in seconds
        headers = kargs.setdefault('headers', {})
        headers.setdefault('User-Agent', _default_user_agent)

        response = self.scraper.get(url, **kargs)
        response.raise_for_status()
        response.encoding = 'utf-8'
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        self.last_visited_url = url.strip('/')
        return response
    # end def

    def post_response(self, url, data={}, headers={}):
        if self._destroyed:
            return None

        headers.setdefault('User-Agent', _default_user_agent)
        headers.setdefault('Content-Type', 'application/json')
        logger.debug('POST url=%s, data=%s, headers=%s', url, data, headers)

        response = self.scraper.post(
            url,
            data=data,
            headers=headers,
            #verify=False,
            #allow_redirects=True,
        )
        response.encoding = 'utf-8'
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        response.raise_for_status()
        return response
    # end def

    def submit_form(self, url, data={}, multipart=False, headers={}):
        '''Submit a form using post request'''
        if self._destroyed:
            return None
        # end if

        content_type = 'application/x-www-form-urlencoded; charset=UTF-8'
        if multipart:
            content_type = 'multipart/form-data'
        # end if
        headers.setdefault('Content-Type', content_type)
        return self.post_response(url, data, headers)
    # end def

    def get_soup(self, *args, **kwargs):
        parser = kwargs.pop('parser', None)
        response = self.get_response(*args, **kwargs)
        return self.make_soup(response, parser)
    # end def

    def make_soup(self, response, parser=None):
        if isinstance(response, Response):
            html = response.content.decode('utf8', 'ignore')
        elif isinstance(response, bytes):
            html = response.decode('utf8', 'ignore')
        elif isinstance(response, str):
            html = str(response)
        else:
            return None
        # end if
        soup = BeautifulSoup(html, parser or 'lxml')
        if not soup.find('body'):
            raise ConnectionError('HTML document was not loaded properly')
        # end if
        return soup
    # end def

    def get_json(self, *args, **kwargs):
        kwargs = kwargs or dict()
        headers = kwargs.setdefault('headers', {})
        headers.setdefault('Accept', 'application/json, text/javascript, */*')
        response = self.get_response(*args, **kwargs)
        return response.json()
    # end def

    def post_soup(self, url, data={}, headers={}, parser='lxml'):
        response = self.post_response(url, data, headers)
        return self.make_soup(response, parser)
    # end def

    def post_json(self, url, data={}, headers={}):
        headers.setdefault('Accept', 'application/json, text/javascript, */*')
        response = self.post_response(url, data, headers)
        return response.json()
    # end def

    def download_cover(self, output_file):
        response = self.get_response(self.novel_cover)
        with open(output_file, 'wb') as f:
            f.write(response.content)
        # end with
    # end def

    # ------------------------------------------------------------------------- #

    blacklist_patterns = [
        r'^[\W\D]*(volume|chapter)[\W\D]+\d+[\W\D]*$',
    ]
    bad_tags = [
        'noscript', 'script', 'iframe', 'form', 'hr', 'img', 'ins',
        'button', 'input', 'amp-auto-ads', 'pirate'
    ]
    block_tags = [
        'h3', 'div', 'p'
    ]

    def is_blacklisted(self, text):
        if len(text.strip()) == 0:
            return True
        # end if
        for pattern in self.blacklist_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
            # end if
        # end for
        return False
    # end def

    def clean_contents(self, div):
        if not div:
            return div
        # end if
        div.attrs = {}
        for tag in div.find_all(True):
            if isinstance(tag, Comment):
                tag.extract()   # Remove comments
            elif tag.name == 'br':
                next_tag = getattr(tag, 'next_sibling')
                if next_tag and getattr(next_tag, 'name') == 'br':
                    tag.extract()
                # end if
            elif tag.name in self.bad_tags:
                tag.extract()   # Remove bad tags
            elif not tag.text.strip():
                tag.extract()   # Remove empty tags
            elif self.is_blacklisted(tag.text):
                tag.extract()   # Remove blacklisted contents
            elif hasattr(tag, 'attrs'):
                tag.attrs = {}    # Remove attributes
            # end if
        # end for
        return div
    # end def

    def extract_contents(self, tag, level=0):
        body = []
        if level == 0:
            self.clean_contents(tag)
        # end if

        for elem in tag.contents:
            if isinstance(elem, Comment):
                continue
            # end if
            if self.block_tags.count(elem.name):
                body += self.extract_contents(elem, level + 1)
                continue
            # end if
            text = ''
            if not elem.name:
                text = str(elem).strip()
            else:
                text = '<%s>%s</%s>'
                text = text % (elem.name, elem.text.strip(), elem.name)
            # end if
            if text:
                body.append(text)
            # end if
        # end for

        if level > 0:
            return body
        else:
            return [x for x in body if len(x.strip())]
        # end if
    # end def

    def cleanup_text(self, text):
        return re.sub(u'[???-??????-??????-????????????-??????-?????????-??????-??????-??????-??????-???]',
                      '', str(text), flags=re.UNICODE)
    # end def
# end class
