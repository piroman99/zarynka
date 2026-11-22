# -*- coding: utf-8 -*-
"""Замер сиденья пропа bench.webp самими пикселями (без зрения).

Логика: у скамейки со спинкой в маске видно ДЫРУ между досками спинки и сиденьем.
Для каждой колонки ищем разрывы в вертикальном профиле непрозрачности; верхний край
доски сиденья = строка сразу ПОД этой дырой. Так получаем линию сиденья по колонкам,
фитим прямую и печатаем угол + точку у ближнего торца.

Второй проход: «доля заполнения» в окне 3x3 — доска сиденья даёт длинный сплошной
горизонтальный прогон, ножки — узкие вертикальные. Печатаем карту для контроля.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
P = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)
m = a[:, :, 3] > 140
Hf, Wf = m.shape
print('файл %dx%d' % (Wf, Hf))


def runs(col):
    out = []
    start = None
    for y in range(len(col)):
        if col[y] and start is None:
            start = y
        elif not col[y] and start is not None:
            out.append((start, y - 1))
            start = None
    if start is not None:
        out.append((start, len(col) - 1))
    return out


print('\nколонка: разрывы в маске (верхние 3 прогона)')
seat_pts = []
for x in range(40, Wf - 40, 20):
    rs = runs(m[:, x])
    print('  x=%3d  прогоны %s' % (x, rs[:(len(rs) if len(rs) <= 4 else 4)]))
    if len(rs) >= 2:
        # дыра между 1-м и 2-м прогоном -> верх 2-го прогона = верх доски сиденья
        gap = rs[1][0] - rs[0][1]
        if 6 <= gap <= 120:
            seat_pts.append((x, rs[1][0]))

if seat_pts:
    pts = np.array(seat_pts, dtype=np.float64)
    A = np.vstack([pts[:, 0], np.ones(len(pts))]).T
    k, b = np.linalg.lstsq(A, pts[:, 1], rcond=None)[0]
    ang = np.degrees(np.arctan2(-k, 1.0))
    print('\nлиния верха сиденья: y = %.4f*x + %.1f, наклон %.1f° вверх-вправо, точек %d'
          % (k, b, ang, len(pts)))
    for x in (60, 200, 400, 600, 800):
        print('  x=%4d -> верх сиденья y=%.0f (доля %.3f)' % (x, k * x + b, (k * x + b) / Hf))
    print('\nдля справки: низ маски (земля у ближнего торца) y=%.0f (доля %.3f)'
          % (m[:, 60:120].any(axis=0).nonzero()[0].max() if False else 0, 0))
    # земля у ближнего левого края
    col = m[:, 100]
    rs = runs(col)
    print('  земля у x=100: низ маски y=%d (доля %.3f)' % (rs[-1][1], rs[-1][1] / Hf))
else:
    print('дыр не нашли — печатаю полный профиль по центру')
    for x in (Wf // 4, Wf // 2, 3 * Wf // 4):
        print('  x=%d %s' % (x, runs(m[:, x])))
