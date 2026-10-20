# -*- coding: utf-8 -*-
"""Числовая проверка кадров перехода: яркость кадра и центра (лого)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for nm in ('dark', 'logo', 'light'):
    p = os.path.join(HERE, 'assets', 'review', 'review_115_trans_%s.png' % nm)
    im = np.asarray(Image.open(p).convert('L'), dtype=np.float32) / 255.0
    h, w = im.shape
    c = im[h // 2 - h // 6:h // 2 + h // 6, w // 2 - w // 6:w // 2 + w // 6]
    print('%-6s кадр %.1fx%.1f  яркость: средняя %.3f  центр %.3f  максимум %.3f'
          % (nm, w, h, im.mean(), c.mean(), im.max()))
