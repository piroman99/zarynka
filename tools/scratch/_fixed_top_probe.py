# -*- coding: utf-8 -*-
"""Что творится в верхних строках исправленного пропа (почему верх торца = 0)."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
P = os.path.join(ROOT, '_sat', 'prop_bench_new_fixed.png')
a = np.asarray(Image.open(P).convert('RGBA'))
m = a[:, :, 3] > 140
print('файл', a.shape[1], 'x', a.shape[0])
for y in range(0, 12):
    idx = np.nonzero(m[y])[0]
    print('  y=%3d  непрозрачных %3d  x %s..%s' % (y, idx.size,
                                                    idx.min() if idx.size else '-',
                                                    idx.max() if idx.size else '-'))

print('\nсуммы по строкам в полосе x 77..397 (первые 20 и ещё несколько):')
for y in list(range(0, 20)) + [60, 80, 100, 120, 140]:
    print('  y=%3d  сумма %3d' % (y, m[y, 77:397].sum()))
