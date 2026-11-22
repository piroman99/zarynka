# -*- coding: utf-8 -*-
"""Профиль новой скамейки по колонкам: где ближний торец (высокий), где дальний (низкий)."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'bench_new_matte.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)
m = a[:, :, 3] > 140
Hf, Wf = m.shape
print('файл %dx%d' % (Wf, Hf))
print(' x%%   x   верх  низ  высота')
for frac in np.arange(0.02, 1.0, 0.05):
    x = int(frac * Wf)
    col = np.nonzero(m[:, x])[0]
    if col.size == 0:
        print(' %3.0f %4d    -    -' % (frac * 100, x))
        continue
    print(' %3.0f %4d  %4d %4d  %4d' % (frac * 100, x, col.min(), col.max(), col.max() - col.min()))
