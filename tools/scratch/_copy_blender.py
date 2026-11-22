# -*- coding: utf-8 -*-
"""Копирует блендер-скрипты из workspace в репозиторий (tools/alley) и проверяет,
что в них нет приватного (IP станции, путей к ключам)."""
import os
import re
import shutil

WS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # workspace
REPO = os.path.join(WS, 'novella', 'zaryanka')
DST = os.path.join(REPO, 'tools', 'alley')
os.makedirs(DST, exist_ok=True)

FILES = ['_bench_blend7.py', '_bench_blend_diag.py']
SECRET = re.compile(r'192\.168\.|\.ssh|home_ed25519|nanobot@|/home/ivan|/home/nanobot')

for name in FILES:
    src = os.path.join(WS, name)
    if not os.path.exists(src):
        print('нет источника:', name)
        continue
    with open(src, encoding='utf-8') as f:
        txt = f.read()
    hits = SECRET.findall(txt)
    if hits:
        print('ОТКАЗ: %s содержит приватное: %s' % (name, sorted(set(hits))))
        continue
    with open(os.path.join(DST, name), 'w', encoding='utf-8') as f:
        f.write(txt)
    print('скопирован %s -> tools/alley/ (%d B)' % (name, os.path.getsize(os.path.join(DST, name))))
