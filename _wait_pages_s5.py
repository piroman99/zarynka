# -*- coding: utf-8 -*-
"""Ждём обновления GitHub Pages: поллим s5.png, пока хеш не совпадёт с локальным."""
import os, time, hashlib, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
local = open(os.path.join(HERE, 'vn2', 'img', 'prolog', 's5.png'), 'rb').read()
want = hashlib.sha256(local).hexdigest()[:16]
url = 'https://piroman99.github.io/zarynka/vn2/img/prolog/s5.png'
print('ждём хеш', want, '| локально', len(local), 'B')

for i in range(12):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'nanobot', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = resp.read()
        got = hashlib.sha256(data).hexdigest()[:16]
        print('%2d) %7d B  %s  %s' % (i + 1, len(data), got, 'OK — новый кадр онлайн' if got == want else 'ещё старый'))
        if got == want:
            break
    except Exception as e:
        print('%2d) FAIL %s %s' % (i + 1, type(e).__name__, e))
    time.sleep(20)
