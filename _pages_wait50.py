# -*- coding: utf-8 -*-
"""Дождаться Pages: новый kate_smile.webp + content.js с эмоциями."""
import os, json, time, urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/'
HERE = os.path.dirname(os.path.abspath(__file__))


def head(url, n):
    req = urllib.request.Request(url + '?x=%d' % n, method='HEAD',
                                 headers={'User-Agent': 'Mozilla/5.0'})
    r = urllib.request.urlopen(req, timeout=30)
    return int(r.headers.get('Content-Length') or 0)


for a in range(30):
    try:
        loc = os.path.getsize(os.path.join(HERE, 'vn2', 'img', 'char', 'kate_smile.webp'))
        rem = head(BASE + 'img/char/kate_smile.webp', a)
        txt = urllib.request.urlopen(urllib.request.Request(
            BASE + 'content.js?x=%d' % a, headers={'User-Agent': 'Mozilla/5.0'}),
            timeout=30).read().decode('utf-8')
        D = json.loads(txt[txt.index('=') + 1:].strip().rstrip(';'))
        kate = list(D['chars']['Екатерина']['emos'])
        print('попытка %d: kate_smile demo=%s local=%d | emos Кати=%s' % (a + 1, rem, loc, kate))
        if rem == loc and 'smile' in kate:
            print('PAGES ОБНОВИЛСЯ')
            break
    except Exception as e:
        print('попытка %d: %s' % (a + 1, e))
    time.sleep(20)
