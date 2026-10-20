# -*- coding: utf-8 -*-
"""Дождаться Pages: новый content.js (emblemVer) + app.js + пятиугольник в trans_logo.png."""
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


loc = {k: md5(open(os.path.join(HERE, 'vn2', k), 'rb').read())
       for k in ('app.js', 'content.js', 'img/trans_logo.png')}
D = json.loads(open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8')
               .read().split('=', 1)[1].strip().rstrip(';'))
want = D['emblemVer']
print('ждём emblemVer =', want)

for a in range(20):
    try:
        cj = get(BASE + 'content.js', a).decode('utf-8')
        Dd = json.loads(cj[cj.index('=') + 1:].strip().rstrip(';'))
        emb = md5(get(BASE + 'img/trans_logo.png', a))
        app = md5(get(BASE + 'app.js', a))
        print('попытка %d: emblemVer=%s (нужно %s) | trans_logo %s | app %s'
              % (a + 1, Dd.get('emblemVer'), want, emb == loc['img/trans_logo.png'],
                 app == loc['app.js']))
        if (Dd.get('emblemVer') == want and emb == loc['img/trans_logo.png']
                and app == loc['app.js']):
            print('PAGES ОБНОВИЛСЯ')
            break
    except Exception as e:
        print('попытка %d: %s' % (a + 1, e))
    time.sleep(20)
