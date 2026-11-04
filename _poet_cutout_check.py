# -*- coding: utf-8 -*-
"""Не съел ли cutout тёмные волосы поэта: сравнение альфы poet.webp с источником.

Признак ошибки — «дыры» внутри фигуры (прозрачные пиксели, окружённые непрозрачными)
и обрезанная макушка: верх альфы должен быть у самой кромки головы.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, 'vn2', 'img', 'char')
SPR = os.path.join(HERE, 'assets', 'sprites')

for name in ('poet', 'poet_interested', 'poet_upset', 'poet_sh', 'sergey', 'kate'):
    p = os.path.join(CH, name + '.webp')
    if not os.path.exists(p):
        print('нет', p)
        continue
    im = Image.open(p)
    a = np.asarray(im.split()[-1]) > 128
    ys, xs = np.nonzero(a)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    # дыры: прозрачное внутри bbox, у которого все 4 соседа в радиусе 3 — непрозрачные
    sub = a[y0:y1 + 1, x0:x1 + 1]
    k = 3
    solid = np.zeros_like(sub)
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            solid |= np.roll(np.roll(sub, dy, 0), dx, 1)
    hole = (~sub) & solid
    # доля «дыр» внутри фигуры
    print('%-18s %s  фигура %dx%d  верх альфы y=%d  дыр внутри %.2f%%  плотность %.0f%%'
          % (name, im.size, x1 - x0 + 1, y1 - y0 + 1, y0, 100 * hole.mean(), 100 * a.mean()))

print('\nисточники (нормированные PNG, фон 205):')
for n in ('poet_ha_neutral', 'poet_ha_interested', 'poet_ha_upset',
          'poet_sh_neutral', 'poet_sh_tired', 'poet_sh_inspired'):
    p = os.path.join(SPR, n + '.png')
    a = np.asarray(Image.open(p).convert('RGB'), np.int16)
    m = np.abs(a - np.array([205, 205, 205])).max(2) > 24
    ys, xs = np.nonzero(m)
    print('  %-18s %s  фигура %dx%d  верх y=%d'
          % (n, Image.open(p).size, xs.max() - xs.min() + 1, ys.max() - ys.min() + 1, ys.min()))
