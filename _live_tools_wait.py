# -*- coding: utf-8 -*-
"""Ждём, пока GitHub Pages отдаст новый app.js (сворачиваемый тулбар, вариант B).

Сравниваем md5 локального и живого файла + ищем маркер варианта B
(комментарий «ряд НЕ сворачивается сам»). Pages отстаёт ~100 с, поэтому поллим.
"""
import os
import sys
import time
import hashlib
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE = 'https://piroman99.github.io/zarynka/vn2/'
FILES = ['app.js', 'style.css', 'index.html']


def md5(b):
    return hashlib.md5(b).hexdigest()


def fetch(url):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache',
                                               'User-Agent': 'nanobot-check'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


local = {}
for f in FILES:
    local[f] = md5(open(os.path.join(HERE, 'vn2', f), 'rb').read())
    print('local %-11s %s' % (f, local[f]))

deadline = time.time() + 420
last = {}
while time.time() < deadline:
    alive = {}
    for f in FILES:
        try:
            alive[f] = md5(fetch(LIVE + f + '?cb=%d' % int(time.time())))
        except Exception as e:
            alive[f] = 'ОШИБКА %r' % e
    last = alive
    ok = all(alive[f] == local[f] for f in FILES)
    print('%s  %s' % (time.strftime('%H:%M:%S'),
                      '  '.join('%s=%s' % (f, 'совпал' if alive[f] == local[f] else alive[f][:10])
                                for f in FILES)), flush=True)
    if ok:
        break
    time.sleep(20)

# маркер варианта B в живом коде
try:
    js = fetch(LIVE + 'app.js?cb=%d' % int(time.time())).decode('utf-8', 'replace')
    print('\nживой app.js: маркер варианта B —', 'ряд НЕ сворачивается сам' in js)
    print('живой app.js: остался ли перехват клика —',
          'document.addEventListener("click", (e) => {' in js and 'setToolsOpen(false);\n  }, true);' in js)
except Exception as e:
    print('маркер проверить не удалось:', e)

ok = all(last.get(f) == local[f] for f in FILES)
print('\nИТОГ: ' + ('PAGES ОТДАЁТ НОВУЮ СБОРКУ' if ok else 'PAGES ЕЩЁ СТАРАЯ'))
sys.exit(0 if ok else 1)
