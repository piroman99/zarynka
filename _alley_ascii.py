# -*- coding: utf-8 -*-
"""ASCII-карта кадра сцены: чем занят каждый участок (мне смотреть без глаз).

Классы по цвету пикселя (HSV + яркость):
  '~' мокрый асфальт (светло-сине-серый, низкая насыщенность, яркий)
  'g' трава/земля (охра-зелёная, тёплая)
  'T' ель/дерево тёмное (зелёно-синее, тёмное)
  'W' дерево скамейки (коричнево-серое, тёмное, низкая насыщенность, R>B)
  '.' небо/бумага (очень светлое)
  '?' прочее
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(GEN, 'alley_b_0.jpg')
COLS = int(sys.argv[2]) if len(sys.argv) > 2 else 96
im = Image.open(path).convert('RGB')
W, H = 1600, 900
im = im.resize((W, H), Image.LANCZOS)
ROWS = int(COLS * H / W * 0.5)


def cls(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    sat = (mx - mn) / max(mx, 1)
    v = (r + g + b) / 3
    if v > 232 and sat < 0.12:
        return '.'
    if g > r + 5 and g > b + 3 and v < 150:
        return 'T'
    if r > b + 18 and r > 95 and v < 185:
        return 'g'
    if v < 120 and sat < 0.30 and r >= b:
        return 'W'
    if b >= r - 6 and sat < 0.22 and v > 120:
        return '~'
    return '?'

cw, ch = W / COLS, H / ROWS
out = []
for ry in range(ROWS):
    line = []
    for rx in range(COLS):
        box = np.asarray(im.crop((int(rx * cw), int(ry * ch), int((rx + 1) * cw), int((ry + 1) * ch))),
                         np.float32).reshape(-1, 3).mean(0)
        line.append(cls(*box))
    out.append(''.join(line))

print('image %s  %dx%d  grid %dx%d' % (os.path.basename(path), W, H, COLS, ROWS))
print('    ' + ''.join(str((i // 10) % 10) for i in range(COLS)))
print('    ' + ''.join(str(i % 10) for i in range(COLS)))
for i, l in enumerate(out):
    print('%3d %s' % (i, l))

# где «дерево скамейки» (W) в нижней половине — грубый bbox
arr = np.array([list(l) for l in out])
half = arr[ROWS // 2:]
ys, xs = np.nonzero(half == 'W')
if len(xs):
    print('\nW (дерево) в нижней половине: x %d..%d  y %d..%d (в клетках; клетка %.1fx%.1f px)'
          % (xs.min(), xs.max(), ys.min() + ROWS // 2, ys.max() + ROWS // 2, cw, ch))
