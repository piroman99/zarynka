# -*- coding: utf-8 -*-
"""Точковая сверка: где на экране стойка и планка спинки, и что в этих пикселях."""
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
DIAG = os.path.join(ROOT, '_sat', 'blend', 'diag.png')

RESX, RESY = 1200, 720
LENS, SENSOR = 50.0, 36.0
F = RESX * LENS / SENSOR
CX, CY, CAMZ, TZ = 1.8903, -3.0, 1.0 / 1.146, 0.45
L, DEPTH, LEG, SLAT_T = 1.80, 0.56, 0.072, 0.034
BACK_X = -DEPTH / 2 + 0.035
TILT = math.radians(10.0)
BACK_SLAT_IN = (LEG + SLAT_T) / 2.0


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


def leg_x(z):
    return BACK_X - z * math.tan(TILT)


a = np.asarray(Image.open(DIAG).convert('RGBA')).astype(int)
rgb, al = a[:, :, :3], a[:, :, 3] > 128


def what(x, y, r=4):
    win = rgb[max(0, y - r):y + r, max(0, x - r):x + r]
    msk = al[max(0, y - r):y + r, max(0, x - r):x + r]
    if not msk.any():
        return 'прозрачно'
    px = win[msk].mean(axis=0)
    if px[0] > px[2] * 1.6:
        return 'КРАСНОЕ (планка) R%d G%d B%d' % tuple(px)
    if px[2] > px[0] * 1.6:
        return 'СИНЕЕ (стойка) R%d G%d B%d' % tuple(px)
    return 'смешанное R%d G%d B%d' % tuple(px)


z = 0.695
yn = -L / 2 + 0.075
leg_axis = (leg_x(z), yn, z)
slat_c = (leg_x(z) + BACK_SLAT_IN * math.cos(TILT), yn, z - BACK_SLAT_IN * math.sin(TILT))
leg_out = (leg_x(z) - LEG / 2 * math.cos(TILT), yn, z + LEG / 2 * math.sin(TILT))
leg_in = (leg_x(z) + LEG / 2 * math.cos(TILT), yn, z - LEG / 2 * math.sin(TILT))

for name, p3 in (('ось стойки', leg_axis), ('наружное ребро стойки', leg_out),
                 ('внутреннее ребро стойки', leg_in), ('центр планки', slat_c)):
    p = proj(p3)
    print('%-22s экран (%6.1f, %6.1f) -> %s' % (name, p[0], p[1],
                                                what(int(p[0]), int(p[1]))))

# сплошной профиль по строке на этой высоте
row = int(proj(leg_axis)[1])
xs = np.nonzero(al[row, :])[0]
print('\nстрока y=%d: непрозрачные x %d..%d' % (row, xs.min(), xs.max()))
seq = []
for x in range(xs.min(), min(xs.max() + 1, xs.min() + 260)):
    px = rgb[row, x]
    seq.append('R' if px[0] > px[2] * 1.6 else ('B' if px[2] > px[0] * 1.6 else '.'))
print('первые 260 px слева:')
print(''.join(seq))
