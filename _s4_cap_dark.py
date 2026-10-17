# -*- coding: utf-8 -*-
"""Доля тёмных пикселей по строкам: так скрим-плашка видна однозначно."""
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
tag = sys.argv[1]
xa, xb, ya, yb = 560, 1120, 460, 700
p = os.path.join(REV, 'review_113_s4_cap_%s.png' % tag)
im = Image.open(p).convert('RGB')
a = np.asarray(im).astype(np.float32)
lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
seg = lum[ya:yb, xa:xb]
dark = (seg < 90).mean(1)
bright = (seg > 180).mean(1)
print('==', tag, '== x %d..%d' % (xa, xb))
rows = []
for i in range(seg.shape[0]):
    y = ya + i
    if dark[i] > 0.55:
        rows.append(y)
    if y % 4 == 0:
        print('%4d dark=%.2f bright=%.2f' % (y, dark[i], bright[i]))
if rows:
    blocks, cur = [], []
    for y in rows:
        if cur and y != cur[-1] + 1:
            blocks.append((cur[0], cur[-1])); cur = []
        cur.append(y)
    if cur:
        blocks.append((cur[0], cur[-1]))
    print('тёмные полосы (dark>55%):', blocks)
