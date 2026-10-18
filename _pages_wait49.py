# -*- coding: utf-8 -*-
"""Дождаться новой сборки на Pages: webp эмоций Сергея должны совпасть по размеру."""
import os, time, urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/img/char/'
HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, 'vn2', 'img', 'char')
NAMES = ['sergey_smile.webp', 'sergey_concerned.webp']


def size(url, n):
    req = urllib.request.Request(url + '?x=%d' % n, method='HEAD',
                                 headers={'User-Agent': 'Mozilla/5.0'})
    r = urllib.request.urlopen(req, timeout=30)
    return int(r.headers.get('Content-Length') or 0)


for a in range(30):
    ok = True
    line = []
    for nm in NAMES:
        loc = os.path.getsize(os.path.join(LOC, nm))
        try:
            rem = size(BASE + nm, a)
        except Exception as e:
            rem = -1
        line.append('%s demo=%s local=%d' % (nm, rem, loc))
        ok = ok and rem == loc
    print('попытка %d: %s' % (a + 1, ' | '.join(line)))
    if ok:
        print('PAGES ОБНОВИЛСЯ')
        break
    time.sleep(20)
