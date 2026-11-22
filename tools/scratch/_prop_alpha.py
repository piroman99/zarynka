# -*- coding: utf-8 -*-
"""Проверка проп-скамейки: сколько в ней «плёнки» (полупрозрачный фон) и где плотное дерево."""
import os
import sys

import numpy as np
from PIL import Image

p = sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/prop_bench.png'
im = Image.open(p)
a = np.asarray(im.split()[-1])
print(p, im.size, im.mode)
print('alpha: 0..8 %.1f%%  8..200 %.1f%%  200..255 %.1f%%'
      % (100 * (a < 8).mean(), 100 * ((a >= 8) & (a < 200)).mean(), 100 * (a >= 200).mean()))
# где полупрозрачные пиксели: по строкам/столбцам
mid = (a >= 8) & (a < 200)
print('полупрозрачные по строкам (каждые 1/12 высоты):')
for k in range(13):
    y = min(im.height - 1, int(im.height * k / 12))
    print('  y %3d%%  %5.1f%%' % (100 * k / 12, 100 * mid[y].mean()))
print('полупрозрачные по столбцам (каждые 1/12 ширины):')
for k in range(13):
    x = min(im.width - 1, int(im.width * k / 12))
    print('  x %3d%%  %5.1f%%' % (100 * k / 12, 100 * mid[:, x].mean()))
