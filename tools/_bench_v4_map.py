# -*- coding: utf-8 -*-
"""ASCII-карта маски скамейки v4 + профиль низа по колонкам с шагом 1%."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'prop_bench_v4_matte.png')

im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
print('file', w, h)
m = a > 140

# ASCII карта 80x44
COLS, ROWS = 80, 44
print('\nкарта маски (#=плотно, .=редко, пробел=пусто):')
for r in range(ROWS):
    y0, y1 = int(h * r / ROWS), int(h * (r + 1) / ROWS)
    line = []
    for c in range(COLS):
        x0, x1 = int(w * c / COLS), int(w * (c + 1) / COLS)
        blk = a[y0:y1, x0:x1]
        dens = (blk > 140).mean()
        line.append('#' if dens > 0.5 else ('+' if dens > 0.15 else ('.' if dens > 0.01 else ' ')))
    print('%4d|%s' % (y0, ''.join(line)))

print('\nпрофиль низа по колонкам 1%:')
vals = []
for c in range(0, 100, 1):
    x0, x1 = int(w * c / 100), max(int(w * (c + 1) / 100), int(w * c / 100) + 1)
    col = m[:, x0:x1].any(axis=1)
    idx = np.nonzero(col)[0]
    bottom = int(idx.max()) if idx.size else -1
    top = int(idx.min()) if idx.size else -1
    vals.append(bottom)
    print('  %2d%% x=%4d  верх %4d  низ %4d  высота %4d' % (c, x0, top, bottom, bottom - top))
print('\nсамый низ файла: %d (высота файла %d)' % (max(vals), h))
