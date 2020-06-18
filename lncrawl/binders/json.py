# -*- coding: utf-8 -*-

import json
import os
import shutil

from lncrawl.app.binder import Binder
from lncrawl.app.context import Context


class JsonBinder(Binder):

    def process(self, ctx: Context):
        json_dir: str = ctx.get_output_path(self.name)
        if os.path.exists(json_dir) and not ctx.keep_old_path:
            shutil.rmtree(json_dir)

        os.makedirs(json_dir, exist_ok=True)

        novel_file = os.path.join(json_dir, "novel.json")
        with open(novel_file, 'w', encoding='utf-8') as fp:
            json.dump(ctx.novel.to_json(), fp)

        author_file = os.path.join(json_dir, "authors.json")
        with open(author_file, 'w', encoding='utf-8') as fp:
            json.dump([a.to_json() for a in ctx.authors], fp)

        volume_dir = os.path.join(json_dir, 'volumes')
        os.makedirs(volume_dir, exist_ok=True)
        for vol in ctx.volumes:
            volume_file = os.path.join(volume_dir, f"{vol.serial:02}.json")
            with open(volume_file, 'w', encoding='utf-8') as fp:
                json.dump(vol.to_json(), fp)

        chapter_dir = os.path.join(json_dir, 'chapters')
        os.makedirs(chapter_dir, exist_ok=True)
        for chap in ctx.chapters:
            chapter_file = os.path.join(chapter_dir, f"{chap.serial:04}.json")
            with open(chapter_file, 'w', encoding='utf-8') as fp:
                json.dump(chap.to_json(), fp)

        meta_file = os.path.join(json_dir, '_meta.json')
        with open(meta_file, 'w', encoding='utf-8') as fp:
            meta_data = {
                'query': ctx.query,
                'toc_url': ctx.toc_url,
                # 'login_id': ctx.login_id,
                # 'login_password': ctx.login_password,
                'language': ctx.language,
                'text_direction': ctx.text_direction,
                'keep_old_path': ctx.keep_old_path,
                'split_book_by_volumes': ctx.split_book_by_volumes,
                'filename_format': ctx.filename_format,
                'binders': ctx.binders,
            }
            json.dump(meta_data, fp)
