# -*- coding: utf-8 -*-
"""Точные границы ТВ-экрана и текущей плашки-подписи в s4.png (1920x1080)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets/final/prolog/s4.png')).convert('RGB')
a = np.asarray(im).astype(np.float32)
W, H = im.size
lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

# вертикальный градиент внутри ТВ -> горизонтальные границы экрана
band = lum[:, 700:1200]
gy = np.abs(np.diff(band, axis=0)).mean(1)
print('top/bottom edge candidates (y, val):')
idx = np.argsort(gy)[-14:]
print(sorted([(int(i), round(float(gy[i]), 1)) for i in idx]))

# горизонтальный градиент внутри ТВ -> вертикальные границы
band2 = lum[200:500, :]
gx = np.abs(np.diff(band2, axis=1)).mean(0)
idx2 = np.argsort(gx)[-14:]
print('left/right edge candidates (x, val):')
print(sorted([(int(i), round(float(gx[i]), 1)) for i in idx2]))

# где сейчас подпись: ищем самую тёмную полосу 600..1000 по x
row = lum[:, 500:1500].mean(1)
print('\nmean lum by y (600..1000):')
for y in range(600, 1001, 20):
    print(y, round(float(row[y]), 1))
