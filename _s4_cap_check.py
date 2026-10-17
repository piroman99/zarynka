# -*- coding: utf-8 -*-
"""Проверка правки S4: где подпись, что с наездом камеры, не лезет ли в #box."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'assets/final/prolog/s4.png')
im = Image.open(p).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

# 1) тёмная плашка-скрим под ТВ (ищем в полосе y 480..760, x 500..1500)
reg = lum[480:760, 480:1500]
mask = reg < 70
ys, xs = np.nonzero(mask)
print('plate bbox (x,y):', xs.min() + 480, ys.min() + 480, xs.max() + 480, ys.max() + 480,
      'n=%d' % len(xs))

# 2) сам текст (светлые пиксели внутри плашки)
y0, y1 = ys.min() + 480, ys.max() + 480
x0, x1 = xs.min() + 480, xs.max() + 480
sub = lum[y0:y1 + 1, x0:x1 + 1]
tm = sub > 170
tys, txs = np.nonzero(tm)
print('text bbox:', x0 + txs.min(), y0 + tys.min(), x0 + txs.max(), y0 + tys.max(),
      '-> size %dx%d' % (txs.max() - txs.min() + 1, tys.max() - tys.min() + 1))

# 3) проекция на наезд камеры: scale to=1.5, origin (0.44, 0.30)
def proj(v, o, s):
    return o + (v - o) * s
for nm, val in (('plate top', (y0) / H), ('plate bottom', (y1) / H),
                ('text top', (y0 + tys.min()) / H), ('text bottom', (y0 + tys.max()) / H)):
    print('%-13s y=%.3f -> на наезде %.3f' % (nm, val, proj(val, 0.30, 1.5)))
print('кадр при наезде: y видно 0.100..0.767, x 0.147..0.813')
print('ТВ-экран 0.305..0.694 по x, 0.144..0.494 по y — целиком в кадре наезда')
