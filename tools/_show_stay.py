# -*- coding: utf-8 -*-
"""Показать, какое именно приватное совпадение осталось в вынесенных файлах."""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(os.path.dirname(ROOT)), '_station_scripts')
PAT = re.compile(r'192\.168\.[0-9.]+|nanobot@[A-Za-z0-9.]+')

names = sorted(os.listdir(SRC))
print('файлов вне репозитория: %d' % len(names))
for n in names[:40]:
    p = os.path.join(SRC, n)
    if not os.path.isfile(p):
        continue
    try:
        with open(p, encoding='utf-8', errors='ignore') as fh:
            txt = fh.read()
    except OSError:
        continue
    hits = sorted(set(PAT.findall(txt)))
    print('  %-42s %s' % (n, ', '.join(hits) if hits else '(совпадений нет)'))
