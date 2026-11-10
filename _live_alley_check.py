# -*- coding: utf-8 -*-
"""Проверка ЖИВОГО Pages после пуша: что именно отдаёт сайт, побайтово против локального."""
import hashlib
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://piroman99.github.io/zarynka/'


def get(url, tries=1):
    last = None
    for _ in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read(), r.status
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(20)
    return None, last


def local_md5(rel):
    p = os.path.join(HERE, rel)
    if not os.path.exists(p):
        return None
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


fails = []
checks = [
    ('vn2/content.js', 'alley2_mix', None),
    ('vn2/style.css', '.sprite.seated{height:88%}', None),
    ('vn2/img/prop/bench.webp', None, 'md5'),
    ('vn2/img/char/poet_seat_smile.webp', None, 'md5'),
    ('vn2/sheet/alley_size.jpg', None, 'size'),
]

for rel, needle, mode in checks:
    data, st = get(BASE + rel, tries=6)
    if data is None:
        print('%-38s НЕ ОТДАЁТСЯ (%s)' % (rel, st))
        fails.append(rel)
        continue
    if needle:
        ok = needle.encode() in data
        print('%-38s %d, ищём %-28s %s' % (rel, st, needle, 'OK' if ok else 'НЕТ'))
        if not ok:
            fails.append('%s: нет %s' % (rel, needle))
    elif mode == 'md5':
        loc = local_md5(rel)
        rem = hashlib.md5(data).hexdigest()
        print('%-38s %d, md5 %s (локально %s)' % (rel, st, rem[:12], (loc or '')[:12]))
        if loc != rem:
            fails.append('%s: md5 не совпал' % rel)
    elif mode == 'size':
        loc = os.path.getsize(os.path.join(HERE, rel))
        print('%-38s %d, %d Б (локально %d)' % (rel, st, len(data), loc))
        if len(data) != loc:
            fails.append('%s: размер не совпал' % rel)

# музыка: проверяем, что файл реально отдаётся (первые 200 КБ)
try:
    req = urllib.request.Request(BASE + 'assets/audio/sketch/alley2_mix.mp3',
                                 headers={'Range': 'bytes=0-204799'})
    with urllib.request.urlopen(req, timeout=40) as r:
        n = len(r.read())
        print('%-38s %d, %d Б (range)' % ('assets/audio/sketch/alley2_mix.mp3', r.status, n))
        if n < 100000:
            fails.append('alley2_mix.mp3: короткий ответ')
except Exception as e:  # noqa: BLE001
    print('музыка не отдаётся:', e)
    fails.append('alley2_mix.mp3: %s' % e)

print('\nИТОГ: ' + ('ЖИВОЙ Pages СОВПАЛ С ЛОКАЛЬНЫМ' if not fails else 'FAIL: ' + '; '.join(fails)))
sys.exit(0 if not fails else 1)
