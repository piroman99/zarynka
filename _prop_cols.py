# -*- coding: utf-8 -*-
"""Профиль пропа-скамейки по колонкам: верх/низ/высота каждые 4 % ширины."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'assets', 'sprites', 'prop_bench.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im.split()[-1])
m = a > 140
h, w = m.shape
ys, xs = np.nonzero(m)
x0, x1 = xs.min(), xs.max()
print('%dx%d, маска x %d..%d y %d..%d' % (w, h, x0, x1, ys.min(), ys.max()))
print('%5s %6s %6s %6s %8s' % ('x', 'x%', 'верх', 'низ', 'высота'))
for k in range(0, 26):
    x = int(x0 + (x1 - x0) * k / 25.0)
    col = np.nonzero(m[:, x])[0]
    if not len(col):
        print('%5d %5.0f%%      -      -        -' % (x, 100.0 * (x - x0) / (x1 - x0)))
        continue
    print('%5d %5.0f%% %6d %6d %8d' % (x, 100.0 * (x - x0) / (x1 - x0),
                                       col.min(), col.max(), col.max() - col.min() + 1))

# самый высокий столбец и его окрестность
heights = []
for x in range(x0, x1 + 1):
    col = np.nonzero(m[:, x])[0]
    if len(col):
        heights.append((x, col.min(), col.max(), col.max() - col.min() + 1))
heights = np.array(heights, float)
i = int(np.argmax(heights[:, 3]))
print('\nмаксимум высоты: x=%d (%.0f%% ширины), верх %.0f, низ %.0f, высота %.0f'
      % (heights[i, 0], 100.0 * (heights[i, 0] - x0) / (x1 - x0),
         heights[i, 1], heights[i, 2], heights[i, 3]))
for d in (-60, -30, 0, 30, 60, 120, 200):
    j = i + d
    if 0 <= j < len(heights):
        print('  x%+4d: верх %4.0f низ %4.0f высота %4.0f'
              % (d, heights[j, 1], heights[j, 2], heights[j, 3]))
