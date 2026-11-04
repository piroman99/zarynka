# -*- coding: utf-8 -*-
"""Подбор порогов матирования: распределение расстояния до цвета фона ВНУТРИ фигуры.

Нужно понять, есть ли у поэта светлые участки (рубашка), которые попадут в «зону фона»
и станут полупрозрачными. Смотрим перцентили d внутри фигуры (без краевого фона).
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(HERE, 'assets', 'sprites')
GEN = os.path.join(HERE, 'assets', 'gen')


def find(name):
    for ext in ('.png', '.jpg'):
        p = os.path.join(GEN, 'poet_%s_0%s' % (name, ext))
        if os.path.exists(p):
            return p
    return None


for key in ('ha_neutral', 'sh_inspired'):
    p = find(key)
    a = np.asarray(Image.open(p).convert('RGB'), np.float32)
    h, w, _ = a.shape
    ring = np.concatenate([a[:8].reshape(-1, 3), a[:int(h * 0.6), :8].reshape(-1, 3),
                           a[:int(h * 0.6), -8:].reshape(-1, 3)])
    bg = np.median(ring, 0)
    d = np.sqrt(((a - bg) ** 2).sum(2))
    # фигура = центр кадра, где заведомо персонаж (без краёв 12%)
    core = d[int(h * 0.12):int(h * 0.95), int(w * 0.12):int(w * 0.88)]
    qs = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
    print('\n%s %dx%d  фон %s' % (key, w, h, bg.round().astype(int).tolist()))
    print('  перцентили d внутри фигуры:',
          ' '.join('%d%%=%.0f' % (q, np.percentile(core, q)) for q in qs))
    for t in (10, 14, 18, 22, 26, 30, 34, 46):
        print('    доля пикселей d<=%-3d: %.3f' % (t, float((core <= t).mean())))
