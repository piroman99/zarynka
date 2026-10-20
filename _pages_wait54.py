# -*- coding: utf-8 -*-
"""Дождаться Pages: новый app.js (версия значка) + круглый trans_logo.png."""
import os
import time
import json
import hashlib
import urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/'
HERE = os.path.dirname(os.path.abspath(__file__))
UA = {'User-Agent': 'Mozilla/5.0'}


def get(url, n):
    return urllib.request.urlopen(urllib.request.Request(
        url + '?x=%d' % n, headers=UA), timeout=30).read()


def md5(b):
    return hashlib.md5(b).hexdigest()


loc_app = md5(open(os.path.join(HERE, 'vn2', 'app.js'), 'rb').read())
loc_emb = md5(open(os.path.join(HERE, 'vn2', 'img', 'trans_logo.png'), 'rb').read())
loc_idx = md5(open(os.path.join(HERE, 'vn2', 'index.html'), 'rb').read())

for a in range(20):
    try:
        app = md5(get(BASE + 'app.js', a))
        emb = md5(get(BASE + 'img/trans_logo.png', a))
        idx = md5(get(BASE + 'index.html', a))
        print('попытка %d: app %s | trans_logo %s | index %s'
              % (a + 1, app == loc_app, emb == loc_emb, idx == loc_idx))
        if app == loc_app and emb == loc_emb and idx == loc_idx:
            print('PAGES ОБНОВИЛСЯ')
            break
    except Exception as e:
        print('попытка %d: %s' % (a + 1, e))
    time.sleep(20)
