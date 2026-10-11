#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Аудит скачанного арта конкурса: размеры/байты, поиск битых заглушек."""
import os, glob
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ('refs/contest_wa', 'refs/contest_full'):
    d = os.path.join(HERE, sub)
    files = sorted(glob.glob(os.path.join(d, '*.jpg')))
    print(f'== {sub}: {len(files)} файлов ==')
    sizes = {}
    real, tiny, bad = [], [], []
    for f in files:
        b = os.path.getsize(f)
        try:
            im = Image.open(f); w, h = im.size
        except Exception as e:
            bad.append((os.path.basename(f), 'ERR', str(e)[:40])); continue
        sizes.setdefault(b, 0); sizes[b] += 1
        rec = (os.path.basename(f), b, f'{w}x{h}')
        if b < 4000 or w < 200:
            tiny.append(rec)
        else:
            real.append(rec)
    print(f'  настоящих (>=200px, >=4КБ): {len(real)}; мелких: {len(tiny)}; битых: {len(bad)}')
    from collections import Counter
    c = Counter(b for _, b, _ in real)
    print('  дублирующиеся размеры среди «настоящих»:', {k: v for k, v in c.items() if v > 1})
    print('  --- настоящие ---')
    for n, b, wh in real:
        print(f'    {n}  {b}B  {wh}')
    if tiny:
        print('  --- мелкие (первые 10) ---')
        for r in tiny[:10]:
            print('   ', r)
    if bad:
        print('  --- битые ---')
        for r in bad[:10]:
            print('   ', r)
