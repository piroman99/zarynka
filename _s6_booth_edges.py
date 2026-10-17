# -*- coding: utf-8 -*-
"""Найти вертикальные стойки будки: считаем градиент по X в области будки и печатаем сильные линии."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
plate = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('L')
plate = plate.resize((2400, 1350), Image.LANCZOS)
a = np.asarray(plate, dtype=np.float32)

X0, X1, Y0, Y1 = 1700, 2400, 250, 700
reg = a[Y0:Y1, X0:X1]
gx = np.abs(np.diff(reg, axis=1)).mean(axis=0)
# сгладим по 3
k = np.convolve(gx, np.ones(5) / 5, mode='same')
idx = np.argsort(k)[::-1][:40]
idx = sorted(set(int(X0 + i) for i in idx))
print('сильные вертикальные линии (x):', idx)
print('по колонкам (топ-20):')
for i in np.argsort(k)[::-1][:20]:
    print('   x=%4d  grad=%.1f' % (X0 + i, k[i]))

gy = np.abs(np.diff(reg, axis=0)).mean(axis=1)
ky = np.convolve(gy, np.ones(5) / 5, mode='same')
print('сильные горизонтальные линии (y):')
for i in np.argsort(ky)[::-1][:14]:
    print('   y=%4d  grad=%.1f' % (Y0 + i, ky[i]))