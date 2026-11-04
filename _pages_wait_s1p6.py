# -*- coding: utf-8 -*-
"""Дождаться GitHub Pages и сверить живые файлы с локальными (md5/size).

    python3 _pages_wait_s1p6.py [--tries=12]

Проверяет: content.js, vn2/img/prolog/s1a.webp, p6.webp, s1.webp,
vn2/audio/vo/s1_00.mp3, s1_01.mp3.
"""
import hashlib
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://piroman99.github.io/zarynka/vn2/'
FILES = ['content.js', 'img/prolog/s1a.webp', 'img/prolog/s1.webp', 'img/prolog/p6.webp',
         'audio/vo/s1_00.mp3', 'audio/vo/s1_01.mp3']

tries = 12
for a in sys.argv[1:]:
    if a.startswith('--tries='):
        tries = int(a.split('=')[1])


def md5(b):
    return hashlib.md5(b).hexdigest()


local = {}
for f in FILES:
    p = os.path.join(HERE, 'vn2', f)
    local[f] = (os.path.getsize(p), md5(open(p, 'rb').read())) if os.path.exists(p) else (0, '')

ok = {}
for attempt in range(1, tries + 1):
    left = [f for f in FILES if f not in ok]
    for f in left:
        try:
            req = urllib.request.Request(BASE + f + '?x=%d' % int(time.time()),
                                         headers={'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(req, timeout=45) as r:
                b = r.read()
        except Exception as e:
            print('  %-24s ошибка %s' % (f, str(e)[:60]))
            continue
        if md5(b) == local[f][1]:
            ok[f] = True
            print('  OK   %-24s %d B' % (f, len(b)))
        else:
            print('  ждём %-24s живой %d B, локальный %d B' % (f, len(b), local[f][0]))
    if len(ok) == len(FILES):
        print('Pages догнал всё (попытка %d)' % attempt)
        break
    time.sleep(20)
print('совпало %d/%d' % (len(ok), len(FILES)))
