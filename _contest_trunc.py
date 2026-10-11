#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка: обрезаны ли JPEG конкурса (нет маркера EOI FFD9)."""
import os, glob
HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ('_probe/refs/contest', 'refs/contest_full'):
    d = os.path.join(HERE, sub)
    files = sorted(glob.glob(os.path.join(d, '*.jpg')))
    tr = 0
    for f in files:
        b = open(f, 'rb').read()
        if not b.endswith(b'\xff\xd9'):
            tr += 1
        if f.endswith(('01_baba-katia.jpg', '14_zvezdnaia-babushka.jpg', '14_1_zvezdnaia-babushka.jpg')):
            print(os.path.basename(f), len(b), 'B  tail=', b[-8:].hex(), ' EOI=', b.endswith(b'\xff\xd9'))
    print(f'{sub}: {tr}/{len(files)} обрезаны (нет FFD9)')
