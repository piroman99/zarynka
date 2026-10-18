# -*- coding: utf-8 -*-
"""Найти 404 на живой демо: разобрать index.html/content.js/app.js, проверить все ассеты."""
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://piroman99.github.io/zarynka/vn2/'

# 1. что лежит в корне Pages
r = urllib.request.urlopen(BASE, timeout=40)
html = r.read().decode('utf-8', 'replace')
print('index.html:', len(html), 'символов')

# 2. локальные пути из content.js и app.js
paths = set()
for fn in ('content.js', 'app.js', 'index.html'):
    txt = open(os.path.join(HERE, 'vn2', fn), encoding='utf-8').read()
    for m in re.findall(r"""['"]([^'"]+\.(?:webp|png|jpg|jpeg|mp3|mp4|ogg|webmanifest|js|css))['"]""", txt):
        if m.startswith(('http', 'data:', 'blob:')):
            continue
        paths.add(m)
print('путей найдено:', len(paths))

bad = []
for p in sorted(paths):
    rel = p.lstrip('./')
    url = BASE + rel
    try:
        rr = urllib.request.urlopen(urllib.request.Request(url, headers={'Cache-Control': 'no-cache'}),
                                    timeout=40)
        rr.read()
    except Exception as e:
        bad.append((rel, getattr(e, 'code', '?'), str(e)[:80]))

print('БИТЫХ:', len(bad))
for rel, code, msg in bad:
    print('  ', code, rel, msg)
