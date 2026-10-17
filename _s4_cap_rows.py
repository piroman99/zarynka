# -*- coding: utf-8 -*-
"""Точный замер плашки в скриншотах: строки скрима (mean<50) + кремовые глифы (>170)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')


def probe(path, xa, xb):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    seg = lum[:, xa:xb]
    mean = seg.mean(1)
    bright = (seg > 170).sum(1)
    rows = [y for y in range(len(mean)) if mean[y] < 55 and bright[y] > 60]
    return im.size, rows


p = os.path.join(REV, 'review_113_s4_cap_zoom.png')
size, rows = probe(p, 620, 1060)
print('zoom', size, 'строк с текстом на скриме:', rows[:3], '...', rows[-3:] if rows else None)
if rows:
    print('   текст: y %d..%d (высота %d px)' % (rows[0], rows[-1], rows[-1] - rows[0] + 1))
    print('   #box верх 641 -> зазор %d px' % (641 - rows[-1]))

p2 = os.path.join(REV, 'review_113_s4_cap_wide.png')
size2, rows2 = probe(p2, 620, 1060)
print('wide', size2, 'сторок:', rows2[:3], '...', rows2[-3:] if rows2 else None)
if rows2:
    print('   текст: y %d..%d (высота %d px)' % (rows2[0], rows2[-1], rows2[-1] - rows2[0] + 1))

p3 = os.path.join(REV, 'review_113_s4_cap_before.png')
size3, rows3 = probe(p3, 620, 1060)
print('before', size3, 'строк:', rows3 if len(rows3) < 30 else (rows3[:3], rows3[-3:]))
