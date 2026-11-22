# -*- coding: utf-8 -*-
"""Что нарисовано в левом-нижнем углу фона: асфальт, газон или пустая бумага."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
im = Image.open(BG).convert('RGB').resize((1920, 1080), Image.LANCZOS)
a = np.asarray(im)

print('проба пикселей (x, y): R G B, яркость, насыщенность')
for y in (900, 950, 1000, 1050, 1075):
    for x in (40, 120, 200, 300, 420, 560, 700, 900):
        r, g, b = (int(v) for v in a[y, x])
        mx, mn = max(r, g, b), min(r, g, b)
        sat = (mx - mn) / mx if mx else 0
        print('  (%4d,%4d)  %3d %3d %3d  ярк %3d  насыщ %.2f' % (x, y, r, g, b, (r + g + b) // 3, sat))

print('\nдоля почти белых пикселей (ярк>238) по полосам:')
for y0 in range(760, 1080, 40):
    band = a[y0:y0 + 40]
    lum = band.mean(axis=2)
    for x0 in range(0, 1920, 240):
        blk = lum[:, x0:x0 + 240]
        print('  y %4d-%4d  x %4d-%4d  белых %4.0f%%' % (y0, y0 + 40, x0, x0 + 240,
                                                        100.0 * (blk > 238).mean()), end='')
    print()
