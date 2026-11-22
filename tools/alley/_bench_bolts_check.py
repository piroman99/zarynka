# -*- coding: utf-8 -*-
"""Проверка: видны ли шляпки винтов на рендере (на спинке и на сиденье).

Проекция центров винтов + сверка яркости пикселя с соседней доской.
"""
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
P = os.path.join(ROOT, '_sat', 'blend', 'bench8.png')

RESX, RESY = 3000, 1800
LENS, SENSOR = 50.0, 36.0
F = RESX * LENS / SENSOR
CX, CY, CAMZ, TZ = 1.8903, -3.0, 1.0 / 1.146, 0.45
L, SEAT_DEPTH, LEG, SLAT_T = 1.80, 0.56, 0.072, 0.034
SEAT_Z = 0.45
T = math.radians(10.0)
BACK_X = -SEAT_DEPTH / 2 + 0.035
POST_Y = L / 2 - 0.075
NS, SW = 4, 0.112
gap = (SEAT_DEPTH - NS * SW) / (NS - 1)
OFF = (LEG + SLAT_T) / 2.0
D = 0.007


def leg_x(z):
    return BACK_X - z * math.tan(T)


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


a = np.asarray(Image.open(P).convert('RGBA'))
rgb, al = a[:, :, :3].astype(float), a[:, :, 3] > 128

pts = []
for z in (0.560, 0.695, 0.830):
    x = leg_x(z) + (OFF + SLAT_T / 2.0 + D / 2.0) * math.cos(T)
    zz = z + (OFF + SLAT_T / 2.0 + D / 2.0) * math.sin(T)
    for sy in (-1, 1):
        pts.append(('спинка z=%.2f y%+d' % (z, sy), (x, sy * POST_Y, zz)))
for i in range(NS):
    x = -SEAT_DEPTH / 2 + SW / 2 + i * (SW + gap)
    for sy in (-1, 1):
        pts.append(('сиденье доск%d y%+d' % (i, sy), (x, sy * POST_Y, SEAT_Z + D / 2.0)))

print('винты: %d' % len(pts))
for name, p3 in pts:
    p = proj(p3)
    x, y = int(round(p[0])), int(round(p[1]))
    if not (0 <= x < RESX and 0 <= y < RESY):
        print('  %-22s за кадром (%6.0f, %6.0f)' % (name, p[0], p[1]))
        continue
    c = rgb[y, x]
    # фон в 2 см слева по доске
    nb = proj((p3[0], p3[1] - 0.035, p3[2]))
    b = rgb[int(round(nb[1])), int(round(nb[0]))]
    lum_c = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    lum_b = 0.299 * b[0] + 0.587 * b[1] + 0.114 * b[2]
    print('  %-22s (%6.0f,%6.0f) цвет R%3.0f G%3.0f B%3.0f ярк %5.1f | доска ярк %5.1f | %s'
          % (name, p[0], p[1], c[0], c[1], c[2], lum_c, lum_b,
             'виден' if abs(lum_c - lum_b) > 12 else 'НЕ виден'))
