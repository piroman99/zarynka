# -*- coding: utf-8 -*-
"""Проверка рендера bench5: где на экране контактируют 4 ножки и совпадает ли это с маской."""
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'blend', 'bench5.png')

RESX, RESY = 3000, 1800
LENS, SENSOR = 50.0, 36.0
F = RESX * LENS / SENSOR
CX, CY, CAMZ, TZ = 1.8903, -3.0, 1.0 / 1.146, 0.45
L, SEAT_DEPTH, LEG = 1.80, 0.56, 0.072
BACK_TOP = 0.90
TILT = math.radians(10.0)


def proj(p3):
    C = np.array([CX, CY, CAMZ], float)
    fwd = np.array([0.0, 0.0, TZ]) - C
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    d = np.array(p3, float) - C
    x, y, z = d @ right, d @ up, d @ fwd
    return np.array([RESX / 2 + F * x / z, RESY / 2 - F * y / z])


im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
m = a > 140
print('файл %dx%d' % (w, h))

pts = {}
for sy, name in ((-1, 'near'), (1, 'far')):
    y = sy * (L / 2 - 0.075)
    pts['footF_' + name] = (SEAT_DEPTH / 2 - LEG / 2, y, 0.0)
    pts['footB_' + name] = (-SEAT_DEPTH / 2 + 0.035, y, 0.0)

for k, v in sorted(pts.items()):
    p = proj(v)
    x, y = int(round(p[0])), int(round(p[1]))
    win = m[max(0, y - 10):y + 10, max(0, x - 10):x + 10]
    print('%-12s (%7.1f, %7.1f) плотных %3.0f%%' % (k, p[0], p[1], 100.0 * win.mean()))

# низ маски по X
bot = np.full(w, -1)
for x in range(w):
    idx = np.nonzero(m[:, x])[0]
    if idx.size:
        bot[x] = idx.max()
print('\nмаска: минимальный y=%d, максимальный y=%d' % (np.nonzero(m.any(axis=1))[0].min(),
                                                       np.nonzero(m.any(axis=1))[0].max()))
for k, v in sorted(pts.items()):
    p = proj(v)
    x = int(round(p[0]))
    print('  у %-12s x=%4d низ маски в этой колонке %d (ожидали %.0f)'
          % (k, x, bot[x], p[1]))
