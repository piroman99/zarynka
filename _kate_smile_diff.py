# -*- coding: utf-8 -*-
"""Катя smile vs база: где именно отличия (должно быть только лицо)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
base = Image.open(os.path.join(GEN, 'kate_overalls_0.png')).convert('RGB')
B = np.asarray(base, np.float32)
h, w, _ = B.shape

for nm, p in [('kate_smile', os.path.join(GEN, '_kate_v2', 'kate_smile__gpt-image-2_0.png')),
              ('kate_sad (эталон поведения)', os.path.join(GEN, 'kate_sad_0.png'))]:
    im = Image.open(p).convert('RGB')
    if im.size != base.size:
        im = im.resize(base.size, Image.LANCZOS)
    A = np.asarray(im, np.float32)
    d = np.abs(A - B).mean(2)
    print('==', nm, 'mean=%.1f >40: %.1f%%' % (d.mean(), 100 * (d > 40).mean()))
    for gy in range(4):
        row = ''
        for gx in range(4):
            cell = d[gy * h // 4:(gy + 1) * h // 4, gx * w // 4:(gx + 1) * w // 4]
            row += '%6.1f' % (100 * (cell > 40).mean())
        print('   ', row)
