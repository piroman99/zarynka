# -*- coding: utf-8 -*-
"""Как устроены ГОТОВЫЕ спрайты каста в vn2/img/char: размер, bbox, доля головы.

Нужно, чтобы поэт нормировался по ТОЙ ЖЕ мерке, иначе он в кадре другого роста.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, 'vn2', 'img', 'char')

for n in sorted(os.listdir(CH)):
    p = os.path.join(CH, n)
    im = Image.open(p)
    if im.mode != 'RGBA':
        print('%-20s %s %s (без альфы)' % (n, im.size, im.mode))
        continue
    m = np.asarray(im.split()[-1]) > 128
    if not m.any():
        print('%-20s %s пустая альфа' % (n, im.size))
        continue
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    bh, bw = y1 - y0, x1 - x0
    head = m[y0:y0 + max(4, int(bh * 0.30))]
    hx = np.nonzero(head.any(0))[0]
    hw = int(hx.max() - hx.min()) if len(hx) else 0
    print('%-20s %s  bbox %dx%d  h/H %.2f  голова %d (голова/W %.3f, голова/bboxH %.3f)'
          % (n, im.size, bw, bh, bh / im.height, hw, hw / im.width, hw / bh))
