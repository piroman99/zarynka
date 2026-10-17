# -*- coding: utf-8 -*-
"""Замер в скриншотах: где подпись и где верх #box, есть ли зазор."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')

for tag in ('wide', 'zoom'):
    p = os.path.join(REV, 'review_113_s4_cap_%s.png' % tag)
    im = Image.open(p).convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]

    # 1) верх #box: длинная красная линия (220,60,60)
    red = (r > 170) & (g < 110) & (b < 110) & (np.abs(g - b) < 60)
    rows = red.sum(1)
    cand = [y for y in range(H) if rows[y] > W * 0.5]
    box_top = min(cand) if cand else None
    print('%s %dx%d: #box верх = %s (%.1f%% высоты)' % (tag, W, H, box_top,
         100.0 * box_top / H if box_top else -1))

    # 2) кремовый текст подписи (тёплый почти белый)
    cream = (r > 205) & (g > 195) & (b > 175) & (r - b > 12) & (r - b < 45) & (np.abs(r - g) < 18)
    ys, xs = np.nonzero(cream)
    lim = box_top if box_top else H
    keep = (ys < lim - 4) & (ys > H * 0.1)
    ys2, xs2 = ys[keep], xs[keep]
    if len(xs2) == 0:
        print('  подпись не найдена выше бокса!')
        continue
    print('  подпись: x %d..%d  y %d..%d  (%dx%d px, %.1f%% высоты)'
          % (xs2.min(), xs2.max(), ys2.min(), ys2.max(),
             xs2.max() - xs2.min() + 1, ys2.max() - ys2.min() + 1,
             100.0 * (ys2.max() - ys2.min() + 1) / H))
    if box_top:
        print('  зазор подпись->#box: %d px' % (box_top - ys2.max()))
