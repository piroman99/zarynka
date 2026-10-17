# -*- coding: utf-8 -*-
"""Нижняя и верхняя кромка звёздного поля ТВ + кромки корпуса."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets/final/prolog/s4.png')).convert('RGB')
a = np.asarray(im).astype(np.float32)
lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
seg = lum[:, 620:1290]
m = seg.mean(1)
print('y : mean lum  (x 620..1290)')
for y in range(505, 585, 2):
    print('%4d %6.1f' % (y, m[y]))
print('--- верх ---')
for y in range(135, 175, 2):
    print('%4d %6.1f' % (y, m[y]))
