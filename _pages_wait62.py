# -*- coding: utf-8 -*-
"""Дождаться Pages: новый style.css (логотип display:block)."""
import os
import time
import hashlib
import urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/'
HERE = os.path.dirname(os.path.abspath(__file__))
UA = {'User-Agent': 'Mozilla/5.0'}


def get(url, n):
    return urllib.request.urlopen(urllib.request.Request(
        url + '?x=%d' % n, headers=UA), timeout=30).read()


loc = open(os.path.join(HERE, 'vn2', 'style.css'), 'rb').read()
loc_md5 = hashlib.md5(loc).hexdigest()
print('локальный style.css: %s, display:block у .logo: %s'
      % (loc_md5[:8], b'.logo{display:block' in loc))

for a in range(20):
    try:
        live = get(BASE + 'style.css', a)
        ok = hashlib.md5(live).hexdigest() == loc_md5
        print('попытка %d: style.css %s' % (a + 1, ok))
        if ok:
            print('PAGES ОБНОВИЛСЯ')
            break
    except Exception as e:
        print('попытка %d: %s' % (a + 1, e))
    time.sleep(20)
