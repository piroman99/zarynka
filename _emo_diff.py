# -*- coding: utf-8 -*-
"""Насколько эмоции Сергея отличаются от базы и ГДЕ: должна меняться только мимика."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
base = Image.open(os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')).convert('RGB')
B = np.asarray(base, np.float32)

for nm in ('sergey_smile_0.jpg', 'sergey_concerned_0.jpg'):
    im = Image.open(os.path.join(GEN, nm)).convert('RGB')
    if im.size != base.size:
        im = im.resize(base.size, Image.LANCZOS)
    A = np.asarray(im, np.float32)
    d = np.abs(A - B).mean(2)
    h, w = d.shape
    # сетка 4x4: где изменения
    print('==', nm, 'mean diff=%.1f, >40: %.1f%%' % (d.mean(), 100 * (d > 40).mean()))
    for gy in range(4):
        row = ''
        for gx in range(4):
            cell = d[gy * h // 4:(gy + 1) * h // 4, gx * w // 4:(gx + 1) * w // 4]
            row += '%6.1f' % (100 * (cell > 40).mean())
        print('   ', row)
