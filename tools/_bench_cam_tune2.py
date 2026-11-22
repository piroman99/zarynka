# -*- coding: utf-8 -*-
"""Второй проход: высота камеры приведена к горизонту кадра (CAMH = 1/1.146 = 0.8726),
чтобы земля рендера совпала с землёй кадра без подгонки масштаба.
Подбираем CX по углу линии передних ножек = 23.6°.
"""
import math

import numpy as np

RESX, RESY = 3000, 1800
LENS, SENSOR = 50.0, 36.0
F = RESX * LENS / SENSOR
CY = -3.0
CAMH = 1.0 / 1.146          # 0.872600
TZ = 0.45
L, SEAT_DEPTH, LEG = 1.80, 0.56, 0.072
TARGET = 23.6


def basis(CX):
    C = np.array([CX, CY, CAMH], float)
    fwd = np.array([0.0, 0.0, TZ]) - C
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return C, fwd, right, up


def proj(P3, CX):
    C, fwd, right, up = basis(CX)
    d = np.array(P3, float) - C
    x, y, z = d @ right, d @ up, d @ fwd
    return np.array([RESX / 2 + F * x / z, RESY / 2 - F * y / z])


def foot_angle(CX):
    yn, yf = -L / 2 + 0.075, L / 2 - 0.075
    a = proj((SEAT_DEPTH / 2 - LEG / 2, yn, 0.0), CX)
    b = proj((SEAT_DEPTH / 2 - LEG / 2, yf, 0.0), CX)
    return math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0]))


def vp_y(CX):
    """y экранной точки схода направления +Y (горизонт)."""
    C, fwd, right, up = basis(CX)
    d = np.array([0.0, 1.0, 0.0], float)
    z = d @ fwd
    return RESY / 2 - F * (d @ up) / z


for cx in [1.6, 1.7, 1.8, 1.85, 1.9, 2.0]:
    print('CX %.2f -> ножки %.2f°, горизонт y %.1f' % (cx, foot_angle(cx), vp_y(cx)))

lo, hi = 1.5, 2.2
for _ in range(50):
    mid = (lo + hi) / 2
    if foot_angle(mid) > TARGET:
        lo = mid
    else:
        hi = mid
print('\nCX = %.4f -> ножки %.2f°, горизонт y = %.2f (RESY=%d)' % (mid, foot_angle(mid), vp_y(mid), RESY))
print('CAMH = %.6f' % CAMH)
