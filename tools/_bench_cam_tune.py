# -*- coding: utf-8 -*-
"""Подбор азимута камеры так, чтобы линия сиденья в рендере шла ровно 23.6°.

Геометрия = _bench_blend3.py (длина по Y, спинка к -X, камера с +X/-Y).
Считаем экранный угол линии передней кромки сиденья (z=0.45) и оси ножек.
"""
import math

import numpy as np

RESX, RESY = 2400, 1500
LENS, SENSOR = 50.0, 36.0
F = RESX * LENS / SENSOR
CAMH, TZ, CY = 0.85, 0.45, -3.0
L, SEAT_DEPTH = 1.80, 0.56
LEG = 0.072

TARGET = 23.6


def proj(P3, CX):
    C = np.array([CX, CY, CAMH], float)
    fwd = np.array([0.0, 0.0, TZ]) - C
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    d = np.array(P3, float) - C
    x, y, z = d @ right, d @ up, d @ fwd
    return np.array([RESX / 2 + F * x / z, RESY / 2 - F * y / z])


def angles(CX):
    yn = -L / 2 + 0.075
    yf = L / 2 - 0.075
    # передняя кромка сиденья
    a = proj((SEAT_DEPTH / 2, yn, 0.45), CX)
    b = proj((SEAT_DEPTH / 2, yf, 0.45), CX)
    seat = math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0]))
    # передние ножки (контакт с землёй)
    c = proj((SEAT_DEPTH / 2 - LEG / 2, yn, 0.0), CX)
    d = proj((SEAT_DEPTH / 2 - LEG / 2, yf, 0.0), CX)
    feet = math.degrees(math.atan2(-(d[1] - c[1]), d[0] - c[0]))
    # спинка (верх планок)
    e = proj((-SEAT_DEPTH / 2 + 0.035 - 0.90 * math.tan(math.radians(10)), yn, 0.90), CX)
    f = proj((-SEAT_DEPTH / 2 + 0.035 - 0.90 * math.tan(math.radians(10)), yf, 0.90), CX)
    top = math.degrees(math.atan2(-(f[1] - e[1]), f[0] - e[0]))
    return seat, feet, top


print('%5s %8s %8s %8s' % ('CX', 'сиденье', 'ножки', 'спинка'))
best = None
for cx in [1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.0, 2.05, 2.1]:
    s, ft, tp = angles(cx)
    print('%5.2f %7.1f° %7.1f° %7.1f°' % (cx, s, ft, tp))
    d = abs(s - TARGET)
    if best is None or d < best[1]:
        best = (cx, d, s, ft, tp)

# уточняем бисекцией
lo, hi = 1.7, 2.1
for _ in range(40):
    mid = (lo + hi) / 2
    if angles(mid)[0] > TARGET:
        lo = mid
    else:
        hi = mid
s, ft, tp = angles(mid)
print('\nточный CX=%.4f -> сиденье %.2f°, ножки %.2f°, спинка %.2f°' % (mid, s, ft, tp))
