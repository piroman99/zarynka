# -*- coding: utf-8 -*-
"""Дождаться, пока GitHub Pages отдаст сборку с кадром p7 (md5 content.js + p7.webp)."""
import hashlib
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://piroman99.github.io/zarynka/vn2/'

local = open(os.path.join(HERE, 'vn2', 'content.js'), 'rb').read()
lm = hashlib.md5(local).hexdigest()
print('локально content.js %d B md5 %s' % (len(local), lm[:10]))
ok = False
for attempt in range(12):
    try:
        with urllib.request.urlopen(BASE + 'content.js?cb=%d' % time.time(), timeout=30) as r:
            data = r.read()
        rm = hashlib.md5(data).hexdigest()
        has_p7 = b'"p7"' in data
        print('попытка %d: %d B md5 %s p7=%s %s'
              % (attempt + 1, len(data), rm[:10], has_p7,
                 'СОВПАЛО' if rm == lm else 'ещё старое'), flush=True)
        if rm == lm:
            ok = True
            break
    except Exception as e:
        print('попытка %d: %s' % (attempt + 1, e), flush=True)
    time.sleep(15)

for name in ('img/prolog/p7.webp', 'audio/vo/p7_00.mp3', 'audio/vo/s2_00.mp3'):
    try:
        req = urllib.request.Request(BASE + name + '?cb=%d' % time.time(), method='HEAD')
        with urllib.request.urlopen(req, timeout=30) as r:
            print('%-24s %s %s B' % (name, r.status, r.headers.get('Content-Length')))
    except Exception as e:
        print('%-24s FAIL %s' % (name, e))
print('ИТОГ:', 'Pages догнал' if ok else 'Pages ещё не отдал сборку')