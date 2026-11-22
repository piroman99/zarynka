# -*- coding: utf-8 -*-
"""Подбор камеры для блендер-рендера скамейки: наклон оси ~23.6°, всё влезает в кадр.

Проекция честная (pinhole): считаем экранные координаты точек скамейки для сетки
(азимут, дистанция) и выбираем ту, где
  * угол между опорами ближней и дальней ножек на экране ~= целевого;
  * габарит с полями внутри кадра;
  * скамейка занимает максимум места в кадре (детализация).
"""
import itertools
import math

import numpy as np

RESX, RESY = 1600, 1000
LENS = 50.0
SENSOR = 36.0
F = RESX * LENS / SENSOR
TARGET_ANG = 23.6
CAMH = 0.88

L, SEAT_DEPTH = 1.80, 0.56
BACK_TOP = 0.90
BACK_TILT = math.radians(10.0)


def corners():
    """ключевые точки в мировых координатах (X длина, Y глубина, Z вверх)."""
    pts = {}
    for sx in (-1, 1):
        pts['footF%d' % sx] = (sx * L / 2, -SEAT_DEPTH / 2, 0.0)
        pts['footB%d' % sx] = (sx * L / 2, SEAT_DEPTH / 2 - 0.05 + 0.45 * math.sin(BACK_TILT), 0.0)
        pts['top%d' % sx] = (sx * L / 2, SEAT_DEPTH / 2 - 0.05 + 0.45 * math.sin(BACK_TILT), BACK_TOP)
        pts['seatF%d' % sx] = (sx * L / 2, -SEAT_DEPTH / 2, 0.45)
        pts['seatB%d' % sx] = (sx * L / 2, SEAT_DEPTH / 2, 0.45)
    return pts


def project(C, T, P):
    C = np.array(C, float)
    fwd = np.array(T, float) - C
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    d = np.array(P, float) - C
    x, y, z = d @ right, d @ up, d @ fwd
    return np.array([RESX / 2 + F * x / z, RESY / 2 - F * y / z])


def evaluate(az_deg, dist, tz=0.52, camh=CAMH):
    az = math.radians(az_deg)
    # азимут 0 = камера строго спереди (по -Y); больше = сдвиг влево по -X
    C = (-dist * math.sin(az), -dist * math.cos(az), camh)
    T = (0.0, 0.0, tz)
    pts = corners()
    scr = {k: project(C, T, v) for k, v in pts.items()}
    xs = np.array([p[0] for p in scr.values()])
    ys = np.array([p[1] for p in scr.values()])
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    near = scr['footF-1']      # ближний торец, передняя ножка
    far = scr['footF1']
    dx, dy = far[0] - near[0], far[1] - near[1]
    ang = math.degrees(math.atan2(-dy, dx))
    top_near, top_far = scr['top-1'], scr['top1']
    ang_top = math.degrees(math.atan2(-(top_far[1] - top_near[1]), top_far[0] - top_near[0]))
    margin = min(x0, y0, RESX - x1, RESY - y1)
    cover = max(x1 - x0, y1 - y0) / max(RESX, RESY)
    return dict(az=az_deg, dist=dist, ang=ang, ang_top=ang_top, margin=margin,
                cover=cover, w=x1 - x0, h=y1 - y0)


rows = []
for az in [10, 15, 20, 25, 30, 35, 40]:
    for dist in [3.0, 3.5, 4.0, 4.5, 5.0, 6.0]:
        rows.append(evaluate(az, dist))

print('%3s %5s %7s %8s %8s %7s' % ('az', 'dist', 'угол', 'угол_сп', 'поле', 'охват'))
for r in rows:
    flag = '*' if abs(r['ang'] - TARGET_ANG) < 2.5 and r['margin'] > 30 else ' '
    print('%2.0f° %4.1f %6.1f° %7.1f° %8.0f %6.2f %s'
          % (r['az'], r['dist'], r['ang'], r['ang_top'], r['margin'], r['cover'], flag))

best = [r for r in rows if abs(r['ang'] - TARGET_ANG) < 2.5 and r['margin'] > 30]
if best:
    b = max(best, key=lambda r: r['cover'])
    print('\nлучший: az=%.0f dist=%.1f  угол %.1f° (спинка %.1f°), поля %.0f px, охват %.2f'
          % (b['az'], b['dist'], b['ang'], b['ang_top'], b['margin'], b['cover']))
