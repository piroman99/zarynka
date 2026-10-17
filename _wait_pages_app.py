# -*- coding: utf-8 -*-
"""Ждём, пока GitHub Pages отдаст новый app.js (сверка хеша с локальным)."""
import os, time, hashlib, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
local = open(os.path.join(HERE, 'vn2', 'app.js'), 'rb').read()
want = hashlib.sha256(local).hexdigest()[:16]
url = 'https://piroman99.github.io/zarynka/vn2/app.js'
print('ждём', want)
for i in range(20):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'nanobot', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
        data = urllib.request.urlopen(req, timeout=45).read()
        got = hashlib.sha256(data).hexdigest()[:16]
        print('%2d) %s %s' % (i + 1, got, 'OK — новый движок онлайн' if got == want else 'ещё старый'))
        if got == want:
            break
    except Exception as e:
        print('%2d) FAIL %s' % (i + 1, e))
    time.sleep(15)
