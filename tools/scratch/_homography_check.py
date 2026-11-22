# -*- coding: utf-8 -*-
"""Проверка гомографии: куда коэффициенты реально отправляют четыре опорные точки."""
import numpy as np


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(matrix, dtype=float)
    B = np.array(pb, dtype=float).reshape(8)
    res = np.linalg.solve(A.T @ A, A.T @ B)
    return res


nb, nf, fb, ff = (133.0, 879.0), (555.0, 995.0), (1050.0, 504.0), (1336.0, 531.0)
SLOPE = np.tan(np.radians(23.6))
fb_t = (fb[0], nb[1] - SLOPE * (fb[0] - nb[0]))
ff_t = (ff[0], nf[1] - SLOPE * (ff[0] - nf[0]))

src = [nb, nf, ff_t, fb_t]
dst = [nb, nf, ff, fb]
c = find_coeffs(src, dst)
print('коэффициенты:', np.round(c, 6))


def apply(co, x, y):
    a, b, cc, d, e, f, g, h = co
    den = g * x + h * y + 1.0
    return ((a * x + b * y + cc) / den, (d * x + e * y + f) / den)


print('\nпроверка: output(цель) -> input(исходник)')
for (tx, ty), (ox, oy) in zip(src, dst):
    mx, my = apply(c, tx, ty)
    print('  цель (%7.1f,%7.1f) -> факт (%7.1f,%7.1f)  ожидалось (%7.1f,%7.1f)'
          % (tx, ty, mx, my, ox, oy))

print('\nкуда уезжают углы кадра:')
for p in ((0, 0), (1407, 0), (1407, 996), (0, 996)):
    print('  %s -> (%.0f, %.0f)' % (p, *apply(c, *p)))
