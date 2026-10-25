# -*- coding: utf-8 -*-
"""Численная проверка звёзд в титрах без scipy: яркие точки vs текст.

Звезда = яркий пиксель, у которого нет ярких соседей дальше 2 px (мелкая изолированная
точка). Текст = крупные яркие кластеры. Считаем по грубой сетке: пиксель яркий и
сумма ярких в окне 5x5 мала -> точка.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SAT = os.path.join(HERE, '_sat')


def boxsum(a, k):
    pad = k // 2
    ap = np.pad(a.astype(np.int32), pad, mode='constant')
    c = ap.cumsum(0).cumsum(1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k])


for name in ('cr_stars_lo', 'cr_stars_mid', 'cr_stars_hi'):
    p = os.path.join(SAT, name + '.png')
    a = np.asarray(Image.open(p).convert('L')).astype(np.int16)
    h, w = a.shape
    bright = a > 110
    k = 7
    neigh = boxsum(bright, k)
    dots = bright & (neigh <= 6)          # одиночная точка (сама себя + 1-2 px ореола)
    text = bright & (neigh > 40)          # тело буквы
    ys, xs = np.nonzero(dots)
    print('%-12s %dx%d  ярких=%.2f%%  точек=%d  текстовых px=%d  точек в верхней трети=%.0f%%'
          % (name, w, h, 100.0 * bright.mean(), int(dots.sum()), int(text.sum()),
             100.0 * (ys < h / 3).mean() if len(ys) else 0))
