# -*- coding: utf-8 -*-
"""Где на самом деле верх доски сиденья в пропе — по прозрачным зазорам между досками.

В пропе (RGBA) над сиденьем идут три доски спинки, между ними — ПРОЗРАЧНЫЕ
зазоры. Значит по колонке: полосы непрозрачного, между ними дырки, а последняя
сплошная область — сиденье. Его верх = искомый seat_top.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'wc', 'prop_0.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
m = a > 60
print('проп %dx%d' % (w, h))

for x in (250, 300, 343, 400, 450):
    col = m[:, x]
    runs = []
    s = None
    for y in range(h + 1):
        v = col[y] if y < h else False
        if v and s is None:
            s = y
        elif not v and s is not None:
            runs.append((s, y - 1))
            s = None
    print('\nx=%d: непрозрачных полос %d' % (x, len(runs)))
    for i, (y0, y1) in enumerate(runs):
        print('   полоса %d: y %3d..%3d  высота %3d' % (i, y0, y1, y1 - y0 + 1))

# для колонки поэта берём верх последней длинной полосы (сиденье)
x = 343
col = m[:, x]
runs = []
s = None
for y in range(h + 1):
    v = col[y] if y < h else False
    if v and s is None:
        s = y
    elif not v and s is not None:
        runs.append((s, y - 1))
        s = None
print('\nколонка поэта x=%d: полосы %s' % (x, runs))
