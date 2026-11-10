# -*- coding: utf-8 -*-
"""Передняя кромка СИДЕНЬЯ по колонкам: низ «толстой» полосы (доска сиденья),
ножки (тонкие полосы) игнорируем. Плюс локальная земля (низ маски) и верх спинки.

Печатаем по колонкам: верх, низ, кромка сиденья и долю
(земля − сиденье) / (земля − верх) — это и есть «на какой высоте сиденье от пола
в долях высоты спинки».
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'assets', 'sprites', 'prop_bench.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im.split()[-1])
m = a > 140
h, w = m.shape
ys, xs = np.nonzero(m)
x0, x1 = xs.min(), xs.max()

THICK = 22


def runs(x):
    col = m[:, x]
    idx = np.nonzero(np.diff(np.concatenate(([0], col.view(np.int8), [0]))))[0]
    out = []
    for i in range(0, len(idx), 2):
        out.append((int(idx[i]), int(idx[i + 1]) - 1))
    return out


print('%5s %6s %6s %7s %7s %7s %7s' % ('x', 'x%', 'верх', 'низ', 'сиденье', 'толщ.', 'доля'))
rows = []
for k in range(0, 41):
    x = int(x0 + (x1 - x0) * k / 40.0)
    r = runs(x)
    if not r:
        continue
    top = r[0][0]
    bot = r[-1][1]
    thick = [rr for rr in r if rr[1] - rr[0] + 1 >= THICK]
    if not thick:
        continue
    seat = thick[-1][1]
    frac = (bot - seat) / float(max(1, bot - top))
    rows.append((x, top, bot, seat, frac))
    print('%5d %5.0f%% %6d %6d %7d %7d %7.3f'
          % (x, 100.0 * (x - x0) / (x1 - x0), top, bot, seat,
             thick[-1][1] - thick[-1][0] + 1, frac))

arr = np.array([[r[0], r[1], r[2], r[3]] for r in rows], float)
near = arr[arr[:, 0] < x0 + 0.35 * (x1 - x0)]
if len(near) > 5:
    k, b = np.polyfit(near[:, 0], near[:, 3], 1)
    print('\nближняя треть: кромка сиденья y = %.4f x + %.1f (наклон %.1f°)'
          % (k, b, np.degrees(np.arctan(k))))
    kt, bt = np.polyfit(near[:, 0], near[:, 1], 1)
    kg, bg_ = np.polyfit(near[:, 0], near[:, 2], 1)
    print('верх спинки  y = %.4f x + %.1f (наклон %.1f°)' % (kt, bt, np.degrees(np.arctan(kt))))
    print('земля        y = %.4f x + %.1f (наклон %.1f°)' % (kg, bg_, np.degrees(np.arctan(kg))))
    for frac in (0.20, 0.25, 0.30):
        xq = x0 + frac * (x1 - x0)
        seat = k * xq + b
        top = kt * xq + bt
        ground = kg * xq + bg_
        print('  на %.0f%% длины: земля %.0f, сиденье %.0f, верх %.0f -> '
              'сиденье на %.3f высоты спинки'
              % (100 * frac, ground, seat, top, (ground - seat) / (ground - top)))
