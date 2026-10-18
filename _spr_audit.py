# -*- coding: utf-8 -*-
"""Проверка спрайтов: размер, доля прозрачного, bbox фигуры."""
import os
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, 'vn2', 'img', 'char')
for f in sorted(os.listdir(D)):
    p = os.path.join(D, f)
    im = Image.open(p)
    a = np.asarray(im.convert('RGBA'))
    al = a[..., 3]
    ys, xs = np.where(al > 8)
    bbox = (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None
    print('%-20s %s %s opaque=%.1f%% bbox=%s'
          % (f, im.size, im.mode, 100 * (al > 8).mean(), bbox))
