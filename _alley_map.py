# -*- coding: utf-8 -*-
"""ASCII-карта кадра: сетка 24x12, буква = преобладающий характер участка.

  D — тёмный (тень, ель в тени)   G — зелёный (ель/трава)   O — тёплый (охра, солнце)
  B — холодный (небо, синий)      W — бумага (светло, бесцветно)   . — средний серый
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')

names = sys.argv[1:] or ['steps_a', 'alley_a', 'alley_b']
COLS, ROWS = 24, 12

for name in names:
    p = None
    for ext in ('.png', '.jpg'):
        q = os.path.join(GEN, name + '_0' + ext)
        if os.path.exists(q):
            p = q
    if not p:
        print(name, 'нет файла')
        continue
    im = Image.open(p).convert('RGB')
    a = np.asarray(im, np.float32)
    h, w, _ = a.shape
    print('\n%s  %dx%d' % (name, w, h))
    for ry in range(ROWS):
        line = ''
        for rx in range(COLS):
            blk = a[ry * h // ROWS:(ry + 1) * h // ROWS, rx * w // COLS:(rx + 1) * w // COLS]
            r, g, b = blk[..., 0].mean(), blk[..., 1].mean(), blk[..., 2].mean()
            mx, mn = max(r, g, b), min(r, g, b)
            lum = (r + g + b) / 3
            sat = (mx - mn) / max(mx, 1)
            if lum < 78:
                ch = 'D'
            elif sat < 0.09 and lum > 205:
                ch = 'W'
            elif g >= r and g >= b and sat > 0.08:
                ch = 'G'
            elif r >= b + 14:
                ch = 'O'
            elif b >= r + 10:
                ch = 'B'
            else:
                ch = '.'
            line += ch
        print('  ' + line)
