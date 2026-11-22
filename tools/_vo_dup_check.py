#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ищем повторы в тексте страниц VN и дубли озвучки по содержимому файлов."""
import hashlib
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(ROOT, 'vn2')
VO = os.path.join(VN2, 'audio', 'vo')


def norm(t):
    t = t.replace('«', '"').replace('»', '"')
    t = re.sub(r'[^0-9A-Za-zА-Яа-яЁё]+', ' ', t)
    return re.sub(r'\s+', ' ', t).strip().lower()


src = open(os.path.join(VN2, 'content.js'), encoding='utf-8').read()
content = json.loads(src[src.index('{'):src.rindex('}') + 1])
import _vo_util as U
segs = U.segments(content)

# 1) повторы текста (по СЕГМЕНТАМ, вкл. реплики в склеенных страницах)
seen = defaultdict(list)
for nid, k, vo, tx, who in segs:
    seen[norm(tx)].append('%s[%d]' % (nid, k))
dups = {t: loc for t, loc in seen.items() if len(loc) > 1}
print('== повторяющийся текст страниц: %d' % len(dups))
for t, loc in dups.items():
    print('  %s  <= %s' % (t[:90], ', '.join(loc)))

# 2) одинаковые файлы озвучки по хешу
h = defaultdict(list)
for f in sorted(os.listdir(VO)):
    if f.endswith('.mp3'):
        h[hashlib.md5(open(os.path.join(VO, f), 'rb').read()).hexdigest()].append(f)
same = {k: v for k, v in h.items() if len(v) > 1}
print('\n== идентичные по содержимому mp3: %d групп' % len(same))
for k, v in same.items():
    print('  %s' % ', '.join(v))

# 3) страницы в порядке показа
print('\n== порядок страниц ==')
for nid, k, vo, tx, who in segs:
    print('%s[%d] vo=%s who=%s | %s' % (nid, k, vo, who, tx[:70]))
