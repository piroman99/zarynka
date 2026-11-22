# -*- coding: utf-8 -*-
"""Точная геометрия правой (дальней) части пропа: где доски, где земля, где нет ножки.

Печатаем по колонкам x >= 55% файла: верх и низ маски, а также строки, где идёт
«плотная доска» (альфа > 200). Нужно, чтобы дорисовать правую переднюю ножку не на глаз.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)
alpha = a[:, :, 3].astype(np.float32)
rgb = a[:, :, :3].astype(np.float32)
Hf, Wf = alpha.shape
m = alpha > 140
print('файл %dx%d' % (Wf, Hf))

print('\n x    верх  низ  плотных строк(альфа>200)  цвет в самой плотной строке')
for x in range(int(Wf * 0.55), int(Wf * 0.96), 25):
    col = m[:, x]
    if not col.any():
        print(' %4d    -    -' % x)
        continue
    idx = np.nonzero(col)[0]
    dense = np.nonzero(alpha[:, x] > 200)[0]
    c = ''
    if dense.size:
        ys = dense[len(dense) // 2]
        c = 'R%3.0f G%3.0f B%3.0f @y=%d' % (rgb[ys, x, 0], rgb[ys, x, 1], rgb[ys, x, 2], ys)
    print(' %4d  %4d %4d   %3d строк %s..%s   %s'
          % (x, idx.min(), idx.max(), dense.size,
             dense.min() if dense.size else '-', dense.max() if dense.size else '-', c))

print('\nправая часть: нижняя граница маски по x (это должна быть «земля»)')
for x in range(int(Wf * 0.6), Wf, 30):
    col = m[:, x]
    if col.any():
        idx = np.nonzero(col)[0]
        print('  x=%4d (%.2f)  низ y=%4d (%.3f)' % (x, x / Wf, idx.max(), idx.max() / Hf))

print('\nцвет существующих ножек (для дорисовки): низкие непрозрачные пиксели слева')
for x in (110, 150, 340, 380):
    col = np.nonzero(m[:, x])[0]
    if col.size:
        y = col.max() - 20
        print('  x=%4d y=%4d  R%3.0f G%3.0f B%3.0f'
              % (x, y, rgb[y, x, 0], rgb[y, x, 1], rgb[y, x, 2]))
