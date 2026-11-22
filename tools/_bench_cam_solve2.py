# -*- coding: utf-8 -*-
"""Подбор камеры: скамейка стоит ВДОЛЬ оси аллеи (длинная сторона по Y),
спинкой к газону (-X), лицом к дороге (+X). Камера сбоку-спереди.

Подбираем (CX, CY, TZ) так, чтобы на экране:
  * ось скамейки (проекция линии ножек) шла ~23.6° вверх-вправо;
  * скамейка целиком в кадре с полями;
  * занимала максимум места.
"""
import math

import numpy as np

RESX, RESY = 1600, 1000
LENS = 50.0
SENSOR = 36.0
F = RESX * LENS / SENSOR
TARGET_ANG = 23.6

L = 1.80
DEPTH = 0.56
BACK_TOP = 0.90
BACK_TILT = math.radians(10.0)


def pts():
    p = {}
    for sy in (-1, 1):
        p['footF%d' % sy] = (DEPTH / 2, sy * L / 2, 0.0)
        p['footB%d' % sy] = (DEPTH / 2 + 0.10, sy * L / 2, 0.0)
        p['seatF%d' % sy] = (DEPTH / 2, sy * L / 2, 0.45)
        p['seatB%d' % sy] = (-DEPTH / 2, sy * L / 2, 0.45)
        p['top%d' % sy] = (-DEPTH / 2 - 0.16, sy * L / 2, BACK_TOP)
    return p


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


def evaluate(CX, CY, TZ, CAMH=0.85, lens=LENS):
    global F
    F = RESX * lens / SENSOR
    C = (CX, CY, CAMH)
    P = pts()
    scr = {k: project(C, (0.0, 0.0, TZ), v) for k, v in P.items()}
    xs = np.array([p[0] for p in scr.values()])
    ys = np.array([p[1] for p in scr.values()])
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    near = (scr['footF-1'] + scr['footB-1']) / 2.0
    far = (scr['footF1'] + scr['footB1']) / 2.0
    ang = math.degrees(math.atan2(-(far[1] - near[1]), far[0] - near[0]))
    ang_seat = math.degrees(math.atan2(-(scr['seatF1'][1] - scr['seatF-1'][1]),
                                       scr['seatF1'][0] - scr['seatF-1'][0]))
    ang_top = math.degrees(math.atan2(-(scr['top1'][1] - scr['top-1'][1]),
                                      scr['top1'][0] - scr['top-1'][0]))
    margin = min(x0, y0, RESX - x1, RESY - y1)
    cover = max(x1 - x0, y1 - y0) / max(RESX, RESY)
    return dict(CX=CX, CY=CY, TZ=TZ, CAMH=CAMH, ang=ang, ang_seat=ang_seat, ang_top=ang_top,
                margin=margin, cover=cover, w=x1 - x0, h=y1 - y0)


rows = []
for CX in [0.9, 1.1, 1.3, 1.5, 1.7, 2.0]:
    for CY in [-2.6, -3.0, -3.4, -3.8, -4.2, -5.0]:
        for TZ in [0.45, 0.52, 0.60]:
            rows.append(evaluate(CX, CY, TZ))

print('%5s %6s %5s %7s %8s %8s %7s %6s' % ('CX', 'CY', 'TZ', 'ось', 'сиденье', 'спинка', 'поле', 'охват'))
for r in rows:
    if abs(r['ang'] - TARGET_ANG) < 6:
        print('%5.1f %6.1f %5.2f %6.1f° %7.1f° %7.1f° %6.0f %6.2f'
              % (r['CX'], r['CY'], r['TZ'], r['ang'], r['ang_seat'], r['ang_top'],
                 r['margin'], r['cover']))

best = [r for r in rows if abs(r['ang'] - TARGET_ANG) < 2.5 and r['margin'] > 25]
if best:
    b = max(best, key=lambda r: r['cover'])
    print('\nЛУЧШИЙ: CX=%.2f CY=%.2f TZ=%.2f camh=%.2f -> ось %.1f°, спинка %.1f°, поля %.0f, охват %.2f'
          % (b['CX'], b['CY'], b['TZ'], b['CAMH'], b['ang'], b['ang_top'], b['margin'], b['cover']))
else:
    print('\nподходящих нет, расширяем сетку')
