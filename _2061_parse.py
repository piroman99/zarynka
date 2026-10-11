#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse les pages du concours «Зарянка» (2061.su / Wayback) -> liste d'oeuvres."""
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp2061')

block_re = re.compile(r'<div class="work">(.*?)</div>\s*</div>\s*</div>', re.S)
slug_re = re.compile(r'iwork/([a-z0-9_\-]+)/')
thumb_re = re.compile(r'<img src="(/media/cache/[0-9a-f/]+\.jpg)"')
title_re = re.compile(r'work__title"><a[^>]*>(.*?)</a>')
author_re = re.compile(r'work__author"[^>]*>\s*(.*?)\s*</a>', re.S)
award_re = re.compile(r'class="award\s*([a-z0-9 ]*)"')

def clean(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    return re.sub(r'\s+', ' ', s).strip()

works = {}
order = []
for p in range(1, 6):
    f = os.path.join(OUT, f'page_{p}.html')
    if not os.path.exists(f):
        continue
    h = open(f, encoding='utf-8', errors='replace').read()
    n_here = 0
    for m in block_re.finditer(h):
        b = m.group(1)
        sm = slug_re.search(b)
        if not sm:
            continue
        slug = sm.group(1)
        thumb = (thumb_re.search(b) or [None, None])[1] if thumb_re.search(b) else None
        title = clean(title_re.search(b).group(1)) if title_re.search(b) else ''
        author = clean(author_re.search(b).group(1)) if author_re.search(b) else ''
        aw = award_re.search(b)
        award = aw.group(1).strip() if aw else ''
        if slug not in works:
            works[slug] = {'slug': slug, 'thumb': thumb, 'title': title,
                           'author': author, 'award': award, 'page': p}
            order.append(slug)
            n_here += 1
    print(f'page {p}: new works {n_here} (total {len(works)})')

json.dump([works[s] for s in order], open(os.path.join(OUT, 'works.json'), 'w'), ensure_ascii=False, indent=1)
print('TOTAL:', len(works))
# repartition prix
from collections import Counter
print(Counter(w['award'] or '(none)' for w in works.values()))
