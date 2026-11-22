# -*- coding: utf-8 -*-
"""Превью пропа на нейтральном фоне + проверка четырёх ножек по правильным точкам."""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NAME = sys.argv[1] if len(sys.argv) > 1 else 'bench5.png'
P = os.path.join(ROOT, '_sat', 'blend', NAME)

RESX, RESY = 3000, 1800
LENS, SENSOR = 50.0, 36.0
F = RESX * LENS / SENSOR
CX, CY, CAMZ, TZ = 1.8903, -3.0, 1.0 / 1.146, 0.45
L, SEAT_DEPTH, LEG = 1.80, 0.56, 0.072
BACK_X = -SEAT_DEPTH / 2 + 0.035
TILT = math.radians(10.0)
BACK_TOP = 0.90
H_LEG = BACK_TOP / math.cos(TILT)


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
al = np.asarray(im)[:, :, 3]
h, w = al.shape
m = al > 140

bot = np.full(w, -1)
for x in range(w):
    idx = np.nonzero(m[:, x])[0]
    if idx.size:
        bot[x] = idx.max()

checks = {
    'передняя ближняя': (SEAT_DEPTH / 2 - LEG / 2, -L / 2 + 0.075, 0.0),
    'задняя ближняя': (BACK_X - H_LEG * math.sin(TILT), -L / 2 + 0.075, 0.0),
    'передняя дальняя': (SEAT_DEPTH / 2 - LEG / 2, L / 2 - 0.075, 0.0),
    'задняя дальняя': (BACK_X - H_LEG * math.sin(TILT), L / 2 - 0.075, 0.0),
}
print('%s: ножки' % NAME)
for k, v in checks.items():
    p = proj(v)
    x, y = int(round(p[0])), int(round(p[1]))
    win = m[max(0, y - 9):y + 9, max(0, x - 9):x + 9]
    print('  %-18s (%7.1f, %7.1f)  плотных %3.0f%%  низ маски в колонке %d'
          % (k, p[0], p[1], 100.0 * win.mean(), bot[min(max(x, 0), w - 1)]))

# превью на мягком фоне
bgc = Image.new('RGBA', (w + 200, h + 200), (238, 240, 236, 255))
bgc.alpha_composite(im, (100, 60))
prev = bgc.convert('RGB')
y0, y1 = np.nonzero(m.any(axis=1))[0][[0, -1]]
x0, x1 = np.nonzero(m.any(axis=0))[0][[0, -1]]
pad = 60
prev = prev.crop((max(0, x0 + 100 - pad), max(0, y0 + 60 - pad),
                  min(prev.width, x1 + 100 + pad), min(prev.height, y1 + 60 + pad)))
prev.thumbnail((1500, 1500), Image.LANCZOS)
out = os.path.join(ROOT, '_sat', 'blend', NAME.replace('.png', '_preview.jpg'))
prev.save(out, quality=93)
print('preview', os.path.relpath(out, HERE), prev.size, os.path.getsize(out), 'B')
