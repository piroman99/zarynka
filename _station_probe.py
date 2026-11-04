# -*- coding: utf-8 -*-
"""Точный bbox базы в арте станции (над линией грунта) — чтобы вырезать её, а не угадывать."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'assets/gen/ok_space_station_0.jpg')
a = np.asarray(Image.open(p).convert('RGB')).astype(np.float32)
h, w, _ = a.shape
lum = a.mean(axis=2)

GROUND = 552                     # ниже этой строки начинается грунт (доля>90 ~1.0)
band = lum[:GROUND]
m = band > 105                   # силуэт базы светлее неба
rows = np.where(m.any(axis=1))[0]
cols = np.where(m.any(axis=0))[0]
print('база: строки %d..%d, столбцы %d..%d (кадр %dx%d, грунт с y=%d)'
      % (rows[0], rows[-1], cols[0], cols[-1], w, h, GROUND))

# где колонки вообще пустые (разрывы силуэта)
empty = [x for x in range(w) if not m[:, x].any()]
print('пустых столбцов в полосе базы:', len(empty), 'диапазон:', (empty[0], empty[-1]) if empty else '-')

# профиль по столбцам: высота силуэта
prof = m.sum(axis=0)
for x in range(0, w, 64):
    print('  x %4d  высота силуэта %3d' % (x, prof[x]))
