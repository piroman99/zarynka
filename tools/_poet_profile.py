# -*- coding: utf-8 -*-
"""Профиль спрайта поэта: ищем линию таза по силуэту.

Для сидящей фигуры в три четверти таз — там, где силуэт резко расширяется
(бёдра уходят вперёд), а ниже идут ноги. Печатаем ширину силуэта по строкам
и границы «плотных» сегментов.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
print('спрайт %dx%d' % (w, h))
m = a > 100
print('\n%%   y     ширина(px)  x_лев  x_прав')
for pct in range(0, 101, 2):
    y = min(h - 1, int(h * pct / 100.0))
    idx = np.nonzero(m[y])[0]
    if idx.size:
        print('%3d %4d %8d %8d %8d' % (pct, y, idx.size, idx.min(), idx.max()))
    else:
        print('%3d %4d %8d' % (pct, y, 0))

# самая широкая строка ищем в верхней половине/средней
widths = m.sum(axis=1)
for lo, hi, lab in ((0.30, 0.75, 'средняя часть'), (0.40, 0.70, 'область бёдер')):
    y0, y1 = int(h * lo), int(h * hi)
    y = y0 + int(np.argmax(widths[y0:y1]))
    print('\nмакс. ширина в %s: y=%d (%.3f доли), ширина %d px' % (lab, y, y / h, widths[y]))
