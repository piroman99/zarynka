# -*- coding: utf-8 -*-
"""Готовность эмоций поэта к cutout(): бордюр, фон, доля фона; плюс размеры кадров."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')

NAMES = ['poet2_b_0.png', 'poet_ha_neutral', 'poet_ha_interested', 'poet_ha_upset',
         'poet_sh_neutral', 'poet_sh_tired', 'poet_sh_inspired']


def f(name):
    if name.endswith('.png'):
        return os.path.join(GEN, name)
    for ext in ('.png', '.jpg'):
        p = os.path.join(GEN, name + '_0' + ext)
        if os.path.exists(p):
            return p
    return None


for n in NAMES:
    p = f(n)
    if not p:
        print('НЕТ', n)
        continue
    a = np.asarray(Image.open(p).convert('RGB'), np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    d = np.abs(a - bg).max(2)
    print('%-22s %4dx%-4d фон %s  разброс бордюра %4.1f  доля фона %.3f  тёмных %.3f'
          % (n, w, h, bg.round().tolist(), border.std(0).mean(),
             float((d < 22).mean()), float((a.mean(2) < 90).mean())))
