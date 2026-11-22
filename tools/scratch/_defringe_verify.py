# -*- coding: utf-8 -*-
"""Проверка, что дефринж не испортил саму картинку: сравнение внутри силуэта."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')


def erode(mask, n=1):
    m = mask.copy()
    for _ in range(n):
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        m = e
    return m


a = np.asarray(Image.open(os.path.join(CHAR, 'poet_seat_upset.webp')).convert('RGBA')).astype(float)
b = np.asarray(Image.open(os.path.join(CHAR, 'poet_seat_upset_fixed.webp')).convert('RGBA')).astype(float)
print('формы:', a.shape, b.shape)

core = erode(a[:, :, 3] > 250, 6)
d = np.abs(a[:, :, :3] - b[:, :, :3]).max(axis=2)
print('внутри силуэта (глубже 6 px от края): пикселей %d' % core.sum())
print('  средняя |Δ| %.2f, 99%% %.1f, максимум %.0f'
      % (d[core].mean(), np.percentile(d[core], 99), d[core].max()))
print('  пикселей с |Δ|>8: %d (%.3f%%)' % ((d[core] > 8).sum(), 100.0 * (d[core] > 8).mean()))

edge = (a[:, :, 3] > 128) & ~erode(a[:, :, 3] > 128, 3)
print('на кромке (до 3 px): средняя |Δ| %.1f (ожидаемо большое — там и правили)'
      % d[edge].mean())

# альфа: не потеряли ли силуэт
print('альфа: было >128 %d, стало >128 %d (дельта %+d)'
      % ((a[:, :, 3] > 128).sum(), (b[:, :, 3] > 128).sum(),
         (b[:, :, 3] > 128).sum() - (a[:, :, 3] > 128).sum()))
