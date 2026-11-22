# -*- coding: utf-8 -*-
"""Проверка ссылок на «мусорные» файлы корня перед их переносом в подкаталоги."""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TARGETS = ['_pv_catalog.json', '_pv_catalog_fresh.json', '_pv_chat_health.txt', '_pv_health.txt',
           '_pv_media-catalog.json', '_tmp_title_16x9_notitles.png', '_tmp_title_16x9_titles.png',
           '_tmp_title_portrait_notitles.png', '_tmp_title_portrait_titles.png', '_vo_dup.txt',
           'scenario.json']

for t in TARGETS:
    pat = re.compile(r'(?<![\w/.-])' + re.escape(t))
    hits = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', '_sat', 'assets', 'out')]
        for f in files:
            if not f.endswith(('.py', '.md', '.json', '.html', '.js', '.txt')):
                continue
            if f == t:
                continue
            p = os.path.join(base, f)
            try:
                if os.path.getsize(p) > 2_000_000:
                    continue
                with open(p, encoding='utf-8', errors='ignore') as fh:
                    if pat.search(fh.read()):
                        hits.append(os.path.relpath(p, ROOT))
            except OSError:
                continue
    print('%-36s ссылок: %-3d %s' % (t, len(hits), ', '.join(hits[:4])))
