# -*- coding: utf-8 -*-
"""Мелкая карта отличий kate_smile vs база (8x8) — где именно изменилось."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
B = np.asarray(Image.open(os.path.join(GEN, 'kate_overalls_0.png')).convert('RGB'), np.float32)
P = os.path.join(GEN, '_kate_v2', 'kate_smile__gpt-image-2_0.png')
im = Image.open(P).convert('RGB')
if im.size != (B.shape[1], B.shape[0]):
    im = im.resize((B.shape[1], B.shape[0]), Image.LANCZOS)
A = np.asarray(im, np.float32)
d = np.abs(A - B).mean(2)
h, w = d.shape
print('карта >40 (8x8), строки сверху вниз:')
for gy in range(8):
    row = ''
    for gx in range(8):
        cell = d[gy * h // 8:(gy + 1) * h // 8, gx * w // 8:(gx + 1) * w // 8]
        row += '%5.1f' % (100 * (cell > 40).mean())
    print('  y%d' % gy, row)
# максимум отличий
iy, ix = np.unravel_index(np.argmax(d), d.shape)
print('самое сильное отличие в точке (x=%.0f%%, y=%.0f%%): %.0f'
      % (100 * ix / w, 100 * iy / h, d[iy, ix]))
