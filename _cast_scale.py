# -*- coding: utf-8 -*-
"""Голова и рост в спрайтах каста: чтобы сверить масштаб поэта с Екатериной."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for f in ['vn2/img/char/kate.webp', 'vn2/img/char/sergey.webp',
          'vn2/img/char/poet_seat_neutral.webp']:
    p = os.path.join(HERE, f)
    if not os.path.exists(p):
        print('нет', f)
        continue
    im = Image.open(p).convert('RGBA')
    a = np.asarray(im.split()[-1])
    m = a > 128
    ys, xs = np.nonzero(m)
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0 + 1
    band = m[y0:y0 + max(2, int(bh * 0.10))]
    cols = np.nonzero(band.any(0))[0]
    hd = cols.max() - cols.min()
    print('%-34s %11s  фигура %4d px (%.3f холста)  голова %3d  голова/холст %.3f'
          % (f, '%dx%d' % im.size, bh, bh / im.height, hd, hd / im.height))
