# -*- coding: utf-8 -*-
"""Где на самом деле плашка в vn2/img/prolog/s4.webp (после грейда и webp)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for name in ('vn2/img/prolog/s4.webp', 'assets/final/prolog/s4.png'):
    im = Image.open(os.path.join(HERE, name)).convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    # скрим = очень тёмные строки в средней трети по x
    seg = lum[:, int(W * 0.30):int(W * 0.70)]
    dark = (seg < 45).mean(1)
    bright = (seg > 190).mean(1)
    rows = [y for y in range(H) if dark[y] > 0.8 and bright[y] < 0.35]
    blocks, cur = [], []
    for y in rows:
        if cur and y != cur[-1] + 1:
            blocks.append((cur[0], cur[-1])); cur = []
        cur.append(y)
    if cur:
        blocks.append((cur[0], cur[-1]))
    print(name, im.size)
    print('   тёмные полосы (y):', [(b0, b1) for b0, b1 in blocks if b1 - b0 > 8])
    print('   доли:', [(round(b0 / H, 3), round(b1 / H, 3)) for b0, b1 in blocks if b1 - b0 > 8])
