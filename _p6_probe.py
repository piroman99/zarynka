# -*- coding: utf-8 -*-
"""Где в p6 горизонт: ищем строку с самым резким переходом по яркости (и по цвету)."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
a = np.asarray(Image.open(os.path.join(HERE, 'assets/final/prolog/p6.png')).convert('RGB'))
a = a.astype(np.float32)
h, w, _ = a.shape
lum = a.mean(axis=2)

row = lum.mean(axis=1)                 # средняя яркость строки
d = np.abs(np.diff(row))
idx = np.argsort(d)[-12:][::-1]
print('самые резкие переходы по строкам:')
for y in idx:
    print('  y=%3d  |Δ|=%.2f  (%0.1f → %0.1f)' % (y, d[y], row[y], row[y + 1]))

# вертикальный профиль по трём колонкам (лево/центр/право)
print('\nпрофиль по колонкам:')
print('  y      left    center   right')
for y in range(0, h, 60):
    print('  %4d   %6.1f %6.1f %6.1f'
          % (y, lum[y, :w // 4].mean(), lum[y, w // 4:w * 3 // 4].mean(), lum[y, w * 3 // 4:].mean()))

# нижняя треть: это грунт? разброс и цвет
low = a[int(h * 0.72):]
print('\nнижняя треть: RGB %.0f/%.0f/%.0f, std %.1f'
      % (low[..., 0].mean(), low[..., 1].mean(), low[..., 2].mean(), low.reshape(-1, 3).std(axis=0).mean()))
top = a[:int(h * 0.25)]
print('верхняя треть: RGB %.0f/%.0f/%.0f, std %.1f'
      % (top[..., 0].mean(), top[..., 1].mean(), top[..., 2].mean(), top.reshape(-1, 3).std(axis=0).mean()))
