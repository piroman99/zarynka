# -*- coding: utf-8 -*-
"""Дождаться Pages: новая сборка (voVer=2, страница 18 с двумя голосами, новый app.js)."""
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


def local(rel):
    return open(os.path.join(HERE, 'vn2', rel), 'rb').read()


for a in range(20):
    try:
        txt = get(BASE + 'content.js', a).decode('utf-8')
        D = json.loads(txt[txt.index('=') + 1:].strip().rstrip(';'))
        nd = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
        pg = nd['pages'][18]
        app = hashlib.md5(get(BASE + 'app.js', a)).hexdigest()
        css = hashlib.md5(get(BASE + 'style.css', a)).hexdigest()
        rec = len(get(BASE + 'audio/vo/rec_22b.mp3', a))
        print('попытка %d: voVer=%s страница18=%s | app %s | css %s | rec_22b %d B'
              % (a + 1, D.get('voVer'), pg.get('vwho'), app == hashlib.md5(local('app.js')).hexdigest(),
                 css == hashlib.md5(local('style.css')).hexdigest(), rec))
        if (D.get('voVer') == 2 and pg.get('vwho') == ['Екатерина', 'narr']
                and app == hashlib.md5(local('app.js')).hexdigest()
                and css == hashlib.md5(local('style.css')).hexdigest()
                and rec == os.path.getsize(os.path.join(HERE, 'vn2', 'audio', 'vo', 'rec_22b.mp3'))):
            print('PAGES ОБНОВИЛСЯ')
            break
    except Exception as e:
        print('попытка %d: %s' % (a + 1, e))
    time.sleep(20)
