# -*- coding: utf-8 -*-
"""ASCII правой (дальней) части пропа крупно: что там нарисовано и где обрыв."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')
a = np.asarray(Image.open(P).convert('RGBA'))
alpha = a[:, :, 3].astype(np.float32)
Hf, Wf = alpha.shape

x0, x1 = int(Wf * 0.66), int(Wf * 0.98)
y0, y1 = int(Hf * 0.10), int(Hf * 0.50)
sub = alpha[y0:y1, x0:x1]
cols, rows = 78, 40
bx, by = sub.shape[1] / cols, sub.shape[0] / rows
print('правая часть: x %d..%d, y %d..%d (файл %dx%d)' % (x0, x1, y0, y1, Wf, Hf))
print('     ' + ''.join(str((i // 10) % 10) for i in range(cols)))
for j in range(rows):
    yy0, yy1 = int(j * by), max(int(j * by) + 1, int((j + 1) * by))
    row = ''
    for i in range(cols):
        xx0, xx1 = int(i * bx), max(int(i * bx) + 1, int((i + 1) * bx))
        v = sub[yy0:yy1, xx0:xx1].mean()
        row += '#' if v >= 200 else (':' if v >= 80 else ('.' if v >= 12 else ' '))
    print('%4d %s' % (y0 + int(j * by), row))

# линия земли в файле (замер по маске ранее): через (121,875) и (966,454)
def ground_y(x):
    return 875 + (x - 121) * (454 - 875) / (966 - 121)


print('\nлиния земли по x (экстраполяция по маске):')
for x in (1000, 1050, 1100, 1150, 1200):
    print('  x=%4d -> земля y=%.0f' % (x, ground_y(x)))
