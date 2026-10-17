# -*- coding: utf-8 -*-
"""Строки с кремовым текстом в s4.png / s4.webp — где реально подпись."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for name in ('assets/final/prolog/s4.png', 'vn2/img/prolog/s4.webp'):
    im = Image.open(os.path.join(HERE, name)).convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    m = (lum > 185) & (r - b > 10) & (r - b < 60) & (np.abs(r - g) < 25)
    rows = m.sum(1)
    hits = [y for y in range(H) if rows[y] > 40]
    blocks, cur = [], []
    for y in hits:
        if cur and y != cur[-1] + 1:
            blocks.append((cur[0], cur[-1])); cur = []
        cur.append(y)
    if cur:
        blocks.append((cur[0], cur[-1]))
    print(name, im.size, '-> полосы текста:', [(y0, y1, round(y0 / H, 3), round(y1 / H, 3)) for y0, y1 in blocks])
