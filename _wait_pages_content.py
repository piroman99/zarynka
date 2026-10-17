# -*- coding: utf-8 -*-
"""Ждём, пока GitHub Pages отдаст новый content.js (хеш = локальному)."""
import os, time, hashlib, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
local = open(os.path.join(HERE, 'vn2', 'content.js'), 'rb').read()
want = hashlib.sha256(local).hexdigest()[:16]
url = 'https://piroman99.github.io/zarynka/vn2/content.js'
print('ждём content.js', want)
ok = False
for i in range(24):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'nanobot', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
        data = urllib.request.urlopen(req, timeout=45).read()
        got = hashlib.sha256(data).hexdigest()[:16]
        webp = b'.webp' in data
        print('%2d) %s webp=%s %s' % (i + 1, got, webp, 'OK' if got == want else 'ещё старый'))
        if got == want:
            ok = True
            break
    except Exception as e:
        print('%2d) FAIL %s' % (i + 1, e))
    time.sleep(15)
print('РЕЗУЛЬТАТ:', 'новый content.js онлайн' if ok else 'не дождались')
