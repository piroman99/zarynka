# -*- coding: utf-8 -*-
"""Полная ASCII-карта рендера + зум на область задней ножки ближнего торца."""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'blend', sys.argv[1] if len(sys.argv) > 1 else 'bench3.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
m = a > 140

COLS, ROWS = 100, 50
print('карта %dx%d:' % (w, h))
for r in range(ROWS):
    y0 = int(h * r / ROWS)
    y1 = max(int(h * (r + 1) / ROWS), y0 + 1)
    line = []
    for c in range(COLS):
        x0 = int(w * c / COLS)
        x1 = max(int(w * (c + 1) / COLS), x0 + 1)
        dens = m[y0:y1, x0:x1].mean()
        line.append('#' if dens > 0.6 else ('+' if dens > 0.25 else ('.' if dens > 0.05 else ' ')))
    print('%4d|%s' % (y0, ''.join(line)))

# зум: область задней ножки ближнего торца
zx0, zx1 = 380, 700
zy0, zy1 = 1150, 1450
print('\nзум x[%d..%d] y[%d..%d] (шаг 10 px):' % (zx0, zx1, zy0, zy1))
for y in range(zy0, zy1, 10):
    row = ''.join('#' if m[y, x] else '.' for x in range(zx0, zx1, 5))
    print('%4d|%s' % (y, row))
