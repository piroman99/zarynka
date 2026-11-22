# -*- coding: utf-8 -*-
"""Есть ли у пропа «плёнка»: альфа в рамке кадра (там должен быть чистый ноль)."""
import os
import sys

import numpy as np
from PIL import Image

p = sys.argv[1] if len(sys.argv) > 1 else 'assets/sprites/prop_bench.png'
a = np.asarray(Image.open(p).split()[-1]).astype(np.int16)
h, w = a.shape
b = 16
for name, patch in (('верх', a[:b]), ('низ', a[-b:]), ('лево', a[:, :b]), ('право', a[:, -b:]),
                    ('угол ЛВ', a[:b, :b]), ('угол ПН', a[-b:, -b:])):
    print('%-8s средняя альфа %5.1f   макс %3d   доля >40: %5.1f%%'
          % (name, patch.mean(), patch.max(), 100 * (patch > 40).mean()))
print()
print('гистограмма альфы (доли %): ', end='')
for lo, hi in ((0, 8), (8, 40), (40, 90), (90, 160), (160, 220), (220, 256)):
    print('%d-%d: %.1f  ' % (lo, hi, 100 * ((a >= lo) & (a < hi)).mean()), end='')
print()
