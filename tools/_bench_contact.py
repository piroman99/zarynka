# -*- coding: utf-8 -*-
"""Решающая проверка контакта: пересекаются ли силуэты поэта и скамейки.

Если поэт стоит/сидит отдельно, пересечения нет. Сидя — таз и задняя часть бёдер
должны перекрывать доску на несколько десятков пикселей по высоте.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
PROP = os.path.join(ROOT, '_sat', 'wc', 'prop_B.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')

Y_H, K = 572.0, 1.146
Y_GROUND_LEG = 960.0
F_FEET = 0.988


def m_of(y):
    return K * (y - Y_H)


def ground_at(y_seat):
    g = y_seat + 0.45 * m_of(y_seat)
    for _ in range(40):
        g = y_seat + 0.45 * m_of(g)
    return g


prop = Image.open(PROP).convert('RGBA')
a = np.asarray(prop)[:, :, 3]
rows = np.nonzero((a > 60).any(axis=1))[0]
cols = np.nonzero((a > 60).any(axis=0))[0]
px = int(round(0.2856 * Y_GROUND_LEG - 108.5 + 15 - cols.min()))
py = int(round(Y_GROUND_LEG - rows.max()))

# доска
pa = np.asarray(prop)[:, :, 3] > 60
seat_y = int(os.environ.get('SEAT_LOCAL', '258'))
print('сиденье в пропе y=%d -> в кадре %d' % (seat_y, py + seat_y))

f_butt = 0.988 - 0.3726 / 1.32
seat_frame = py + seat_y
ground = ground_at(seat_frame)
h_px = (ground - seat_frame) / (F_FEET - f_butt)
print('земля %.1f, H %.1f px' % (ground, h_px))

poet = Image.open(POET).convert('RGBA')
w = max(1, round(poet.width * h_px / poet.height))
poet = poet.resize((w, int(round(h_px))), Image.LANCZOS)
top = int(round(ground - F_FEET * h_px))
x_poet = int(os.environ.get('POET_X', '421'))
pl = x_poet - poet.width // 2

canvas_bench = Image.new('L', (1920, 1080), 0)
canvas_bench.paste(prop.split()[3], (px, py))
canvas_poet = Image.new('L', (1920, 1080), 0)
canvas_poet.paste(poet.split()[3], (pl, top))
b = np.asarray(canvas_bench) > 60
pp = np.asarray(canvas_poet) > 60
inter = b & pp
print('пересечение силуэтов: %d px' % inter.sum())
if inter.sum():
    ys, xs = np.nonzero(inter)
    print('  y %d..%d, x %d..%d' % (ys.min(), ys.max(), xs.min(), xs.max()))
    # высота перекрытия в самой населённой колонке
    per_col = inter.sum(axis=0)
    xc = int(np.argmax(per_col))
    ysc = np.nonzero(inter[:, xc])[0]
    print('  колонка x=%d: перекрытие по y %d..%d (%d px)' % (xc, ysc.min(), ysc.max(), ysc.size))
else:
    print('  КОНТАКТА НЕТ — фигура и скамейка не перекрываются')

# где низ силуэта поэта и где линия доски
poet_bottom = int(np.nonzero(pp.any(axis=1))[0].max())
print('низ силуэта поэта %d, земля %.0f, доска %d' % (poet_bottom, ground, seat_frame))
