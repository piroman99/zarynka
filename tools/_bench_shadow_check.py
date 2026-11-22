# -*- coding: utf-8 -*-
"""Проверка, что контактная тень легла: сравнение яркости под скамейкой с фоном."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
FULL = os.path.join(ROOT, '_sat', 'blend2_full.jpg')

a = np.asarray(Image.open(BG).convert('RGB').resize((1920, 1080), Image.LANCZOS)).astype(float)
b = np.asarray(Image.open(FULL).convert('RGB')).astype(float)

for y0, y1, lab in ((940, 975, 'прямо под ножками'), (975, 1010, 'ниже'), (900, 940, 'уровень ножек')):
    d = (b[y0:y1, 100:940].mean()) - (a[y0:y1, 100:940].mean())
    print('%-18s средняя дельта RGB %+.1f' % (lab, d))
    row = b[y0:y1, 100:940].mean(axis=(0, 2))
    row0 = a[y0:y1, 100:940].mean(axis=(0, 2))
    print('   минимум яркости %d, фон %d' % (row.min(), row0.mean()))
