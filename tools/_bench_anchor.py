# -*- coding: utf-8 -*-
"""Опорные точки рендера bench3.png: аналитическая проекция + сверка с маской.

Даёт для посадки в кадр:
  NEAR_FOOT  экранная точка контакта передней ножки ближнего торца с землёй
  NEAR_TOP   верхняя точка ближнего торца (спинка, z = 0.90)
  K_RENDER   px на метр по вертикали на ближнем торце
  NEAR_LEFT  левый край маски (для контроля)
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'blend', sys.argv[1] if len(sys.argv) > 1 else 'bench3.png')

RESX, RESY = 2400, 1500
LENS, SENSOR = 50.0, 36.0
CX, CY, CAMH, TZ = 2.00, -3.00, 0.85, 0.45
L, SEAT_DEPTH, BACK_TOP = 1.80, 0.56, 0.90
LEG = 0.072

F = RESX * LENS / SENSOR


def proj(P3):
    C = np.array([CX, CY, CAMH], float)
    fwd = np.array([0.0, 0.0, TZ]) - C
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    d = np.array(P3, float) - C
    x, y, z = d @ right, d @ up, d @ fwd
    return np.array([RESX / 2 + F * x / z, RESY / 2 - F * y / z])


near_front = proj((SEAT_DEPTH / 2 - LEG / 2, -L / 2 + 0.075, 0.0))
near_back = proj((-SEAT_DEPTH / 2 + 0.035, -L / 2 + 0.075, 0.0))
near_top = proj((-SEAT_DEPTH / 2 + 0.035 - BACK_TOP * math.tan(math.radians(10)),
                 -L / 2 + 0.075, BACK_TOP))
far_front = proj((SEAT_DEPTH / 2 - LEG / 2, L / 2 - 0.075, 0.0))
near_seat = proj((SEAT_DEPTH / 2 - 0.05, -L / 2 + 0.075, 0.45))

print('проекция (px):')
for name, pt in (('near_front', near_front), ('near_back', near_back), ('near_top', near_top),
                 ('far_front', far_front), ('near_seat', near_seat)):
    print('  %-10s (%7.1f, %7.1f)  доли (%.3f, %.3f)' % (name, pt[0], pt[1], pt[0] / RESX, pt[1] / RESY))

k_render = (near_front[1] - near_top[1]) / BACK_TOP
print('\nK_RENDER по вертикали ближнего торца: %.3f px/м' % k_render)
print('угол оси: %.1f°' % math.degrees(math.atan2(-(far_front[1] - near_front[1]),
                                                far_front[0] - near_front[0])))

# сверка с маской
im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
m = a > 140
print('\nфайл %dx%d (ожидали %dx%d)' % (w, h, RESX, RESY))
xs = np.nonzero(m.any(axis=0))[0]
ys = np.nonzero(m.any(axis=1))[0]
print('маска bbox x[%d..%d] y[%d..%d]' % (xs.min(), xs.max(), ys.min(), ys.max()))

for name, pt in (('near_front', near_front), ('near_back', near_back),
                 ('far_front', far_front)):
    x, y = int(round(pt[0])), int(round(pt[1]))
    win = m[max(0, y - 14):y + 14, max(0, x - 14):x + 14]
    print('  %-10s окрестность 28x28: плотных %.0f%%' % (name, 100.0 * win.mean()))
