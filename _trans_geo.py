# -*- coding: utf-8 -*-
"""Геометрия лого в кадре перехода: где светлое пятно и какого оно размера."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'assets', 'review', 'review_115_trans_logo.png')
im = np.asarray(Image.open(p).convert('L'), dtype=np.float32) / 255.0
h, w = im.shape
# тулбар справа сверху не мешает: смотрим только центральную треть
y0, y1 = int(h * 0.25), int(h * 0.75)
x0, x1 = int(w * 0.25), int(w * 0.75)
c = im[y0:y1, x0:x1]
mask = c > 0.35
ys, xs = np.nonzero(mask)
if len(ys):
    print('светлое пятно: %d px, bbox %dx%d, центр (%d, %d) из (%dx%d)'
          % (mask.sum(), xs.max() - xs.min() + 1, ys.max() - ys.min() + 1,
             x0 + (xs.min() + xs.max()) // 2, y0 + (ys.min() + ys.max()) // 2, w, h))
    print('средняя яркость пятна %.3f, вне пятна %.3f'
          % (c[mask].mean(), c[~mask].mean()))
else:
    print('светлого пятна нет — лого не видно')
