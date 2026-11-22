# -*- coding: utf-8 -*-
"""Что за бледная вертикаль в правой части пропа: ножка или ореол вырезания."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')
a = np.asarray(Image.open(P).convert('RGBA')).astype(np.float32)
alpha, rgb = a[:, :, 3], a[:, :, :3]

print('цвет и альфа в правой части (x>1100, y 230..490), шаг 20 px:')
for x in range(1100, 1270, 20):
    for y in (250, 300, 350, 400, 450):
        al = alpha[y, x]
        r, g, b = rgb[y, x]
        print('  x=%4d y=%3d  альфа %5.1f  R%3.0f G%3.0f B%3.0f' % (x, y, al, r, g, b))
    print()

print('для сравнения — плотная левая ножка (x 130..200, y 600..860):')
for x in (150, 170, 330, 360):
    for y in (700, 800, 850):
        al = alpha[y, x]
        r, g, b = rgb[y, x]
        print('  x=%4d y=%3d  альфа %5.1f  R%3.0f G%3.0f B%3.0f' % (x, y, al, r, g, b))
