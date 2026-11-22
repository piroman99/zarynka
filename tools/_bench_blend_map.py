# -*- coding: utf-8 -*-
"""ASCII-карта рендера скамейки + поиск четырёх ножек (низ маски)."""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'blend', sys.argv[1] if len(sys.argv) > 1 else 'bench2.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
m = a > 140

COLS, ROWS = 96, 40
xs = np.nonzero(m.any(axis=0))[0]
ys = np.nonzero(m.any(axis=1))[0]
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print('bbox x[%d..%d] y[%d..%d]' % (x0, x1, y0, y1))
print('карта (обрезана по bbox):')
for r in range(ROWS):
    ya = y0 + int((y1 - y0) * r / ROWS)
    yb = y0 + max(int((y1 - y0) * (r + 1) / ROWS), int((y1 - y0) * r / ROWS) + 1)
    line = []
    for c in range(COLS):
        xa = x0 + int((x1 - x0) * c / COLS)
        xb = x0 + max(int((x1 - x0) * (c + 1) / COLS), int((x1 - x0) * c / COLS) + 1)
        dens = m[ya:yb, xa:xb].mean()
        line.append('#' if dens > 0.6 else ('+' if dens > 0.25 else ('.' if dens > 0.05 else ' ')))
    print('%4d|%s' % (ya, ''.join(line)))

# опоры: локальные максимумы низа
bot = np.full(w, -1)
for x in range(w):
    idx = np.nonzero(m[:, x])[0]
    if idx.size:
        bot[x] = idx.max()
runs = []
s = None
for x in range(w + 1):
    v = (x < w) and (bot[x] > y1 - 0.06 * (y1 - y0)) and bot[x] > 0
    if v and s is None:
        s = x
    elif not v and s is not None:
        if x - s >= 8:
            runs.append((s, x - 1))
        s = None
print('\nнижние полосы (ножки, 6%% от низа):')
for s, e in runs:
    print('  x %d..%d  ширина %d  центр %d  низ %d' % (s, e, e - s + 1, (s + e) // 2,
                                                       int(bot[(s + e) // 2])))
if len(runs) >= 2:
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            ci, cj = (runs[i][0] + runs[i][1]) / 2.0, (runs[j][0] + runs[j][1]) / 2.0
            bi, bj = bot[int(ci)], bot[int(cj)]
            ang = np.degrees(np.arctan2(-(bj - bi), cj - ci))
            print('  %d-%d: dx %.0f dy %.0f -> %.1f°' % (i, j, cj - ci, bj - bi, ang))
