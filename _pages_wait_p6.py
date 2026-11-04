# -*- coding: utf-8 -*-
"""Дождаться, пока GitHub Pages отдаст сборку с кадром p6 (md5 content.js + p6.webp)."""
import hashlib
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://piroman99.github.io/zarynka/vn2/'

local = open(os.path.join(HERE, 'vn2', 'content.js'), 'rb').read()
lm = hashlib.md5(local).hexdigest()
print('локально content.js %d B md5 %s' % (len(local), lm[:10]))

for attempt in range(12):
    try:
        with urllib.request.urlopen(BASE + 'content.js?cb=%d' % time.time(), timeout=30) as r:
            data = r.read()
        rm = hashlib.md5(data).hexdigest()
        has_p6 = b'"p6"' in data
        print('попытка %d: %d B md5 %s p6=%s %s'
              % (attempt + 1, len(data), rm[:10], has_p6,
                 'СОВПАЛО' if rm == lm else 'ещё старое'))
        if rm == lm:
            break
    except Exception as e:
        print('попытка %d: %s' % (attempt + 1, e))
    time.sleep(15)

for name in ('img/prolog/p6.webp', 'audio/vo/p6_00.mp3'):
    try:
        req = urllib.request.Request(BASE + name, method='HEAD')
        with urllib.request.urlopen(req, timeout=30) as r:
            print('%-24s %s %s B' % (name, r.status, r.headers.get('Content-Length')))
    except Exception as e:
        print('%-24s FAIL %s' % (name, e))
