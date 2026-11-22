# -*- coding: utf-8 -*-
"""Сверка живого GitHub Pages с локальным файлом репозитория: побайтово.

Pages отстаёт от пуша на 3–8 минут, поэтому по умолчанию ждём и повторяем.

    python3 tools/_pages_check.py                       # vn2/content.js (по умолчанию)
    python3 tools/_pages_check.py vn2/img/char/poet.webp
    python3 tools/_pages_check.py vn2/app.js --wait 600  # ждать до 10 минут

Код возврата 0 — файл совпал побайтово, 1 — не дождались.
"""
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = 'https://piroman99.github.io/zarynka/'

args = [a for a in sys.argv[1:] if not a.startswith('--')]
rel = args[0] if args else 'vn2/content.js'
wait = 480
if '--wait' in sys.argv:
    wait = int(sys.argv[sys.argv.index('--wait') + 1])
if rel.startswith('/'):
    rel = rel[1:]

local_path = os.path.join(ROOT, rel)
if not os.path.exists(local_path):
    print('нет локального файла %s' % rel)
    sys.exit(2)
with open(local_path, 'rb') as f:
    local = f.read()
url = BASE + rel
print('локально: %s — %d B' % (rel, len(local)))

deadline = time.time() + wait
attempt = 0
while True:
    attempt += 1
    try:
        req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache',
                                                  'User-Agent': 'nanobot-check'})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        if data == local:
            print('попытка %d: живой файл %d B — совпал побайтово' % (attempt, len(data)))
            sys.exit(0)
        print('попытка %d: живой файл %d B, локальный %d B — ещё старое'
              % (attempt, len(data), len(local)))
    except Exception as e:
        print('попытка %d: %s: %s' % (attempt, type(e).__name__, e))
    if time.time() + 45 > deadline:
        break
    time.sleep(45)
print('Pages не обновился за %d с (отставание 3–8 минут — норма, повторите позже)' % wait)
sys.exit(1)
