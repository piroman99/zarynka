# -*- coding: utf-8 -*-
"""Какого цвета фон у новой генерации (v3) и где границы предмета."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'assets', 'gen', 'prop_bench_v3_0.png')
a = np.asarray(Image.open(P).convert('RGB')).astype(np.int32)
Hf, Wf = a.shape[:2]
print('файл %dx%d' % (Wf, Hf))
print('\nцвет по углам и центру:')
for name, (x, y) in (('лев-верх', (10, 10)), ('прав-верх', (Wf - 10, 10)),
                     ('лев-низ', (10, Hf - 10)), ('прав-низ', (Wf - 10, Hf - 10)),
                     ('центр', (Wf // 2, Hf // 2))):
    r, g, b = a[y, x]
    print('  %-9s (%4d,%4d)  R%3d G%3d B%3d  ярк %3d' % (name, x, y, r, g, b, (r + g + b) // 3))

lum = a.mean(axis=2)
print('\nгистограмма яркости:')
hist, edges = np.histogram(lum, bins=10, range=(0, 255))
for i, h in enumerate(hist):
    print('  %3d..%3d: %7d px (%.1f%%)' % (int(edges[i]), int(edges[i + 1]), h,
                                           100.0 * h / lum.size))
print('\nдоля пикселей ярче 225: %.1f%%' % (100.0 * (lum > 225).mean()))
print('доля пикселей ярче 200: %.1f%%' % (100.0 * (lum > 200).mean()))

print('\nстрока y=5: цвет в 5 точках')
for x in (100, 600, 900, 1200, 1500):
    r, g, b = a[5, x]
    print('  x=%4d  R%3d G%3d B%3d' % (x, r, g, b))
