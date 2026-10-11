#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Полный аудит всех скачанных артов конкурса + что внутри «битых»."""
import os, glob, hashlib
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
roots = ['_probe/refs/contest', 'refs/contest', 'refs/contest_full', 'refs/contest_wa']
for sub in roots:
    d = os.path.join(HERE, sub)
    files = sorted(glob.glob(os.path.join(d, '*.jpg'))) + sorted(glob.glob(os.path.join(d, '*.png')))
    if not os.path.isdir(d):
        print(f'== {sub}: НЕТ ДИРЕКТОРИИ =='); continue
    print(f'== {sub}: {len(files)} файлов ==')
    real, bad = [], []
    for f in files:
        try:
            im = Image.open(f); w, h = im.size; b = os.path.getsize(f)
            real.append((os.path.basename(f), b, f'{w}x{h}'))
        except Exception:
            bad.append(f)
    print(f'  OK: {len(real)}  битых: {len(bad)}')
    for n, b, wh in real:
        print(f'    {n}  {b}B  {wh}')
    if bad:
        f0 = bad[0]
        print('   первый битый:', os.path.basename(f0), os.path.getsize(f0), 'B')
        with open(f0, 'rb') as fh:
            head = fh.read(200)
        print('   head:', head[:120])

# заглушки 16061?
d = os.path.join(HERE, 'refs/contest_full')
h = {}
for f in glob.glob(os.path.join(d, '*.jpg')):
    if os.path.getsize(f) == 16061:
        h.setdefault(hashlib.md5(open(f, 'rb').read()).hexdigest(), []).append(os.path.basename(f))
print('== contest_full: уникальных картинок среди 16061-байтных ==', len(h))
for k, v in h.items():
    print('   ', k[:10], len(v), 'шт:', v[:3])
