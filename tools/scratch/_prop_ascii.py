# -*- coding: utf-8 -*-
"""ASCII-карта маски пропа bench.webp — чтобы «увидеть» скамейку кодом.

Символы: '.' — почти прозрачно, ':' — полупрозрачно, '#' — плотно (>=200).
Печатаем 100 колонок x 48 строк с номерами строк файла (925x700).
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
P = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)
alpha = a[:, :, 3].astype(np.float32)
Hf, Wf = alpha.shape

cols, rows = 100, 48
bx, by = Wf / cols, Hf / rows
print('маска bench.webp %dx%d, 100 колонок, строки подписаны' % (Wf, Hf))
print('     ' + ''.join(str((i // 10) % 10) for i in range(cols)))
for j in range(rows):
    y0, y1 = int(j * by), max(int(j * by) + 1, int((j + 1) * by))
    row = ''
    for i in range(cols):
        x0, x1 = int(i * bx), max(int(i * bx) + 1, int((i + 1) * bx))
        v = alpha[y0:y1, x0:x1].mean()
        row += '#' if v >= 200 else (':' if v >= 80 else ('.' if v >= 12 else ' '))
    print('%4d %s' % (int(j * by), row))

# цвет: где коричневое дерево (R>G>B), где что
print('\nсредний цвет по горизонтальным полосам (доля непрозрачных, RGB):')
for j in range(0, rows, 2):
    y0, y1 = int(j * by), max(int(j * by) + 1, int((j + 2) * by))
    blk = a[y0:y1]
    sel = blk[:, :, 3] > 140
    if sel.sum() < 50:
        continue
    c = blk[sel][:, :3].mean(axis=0)
    print('  y %3d-%3d  покрытие %4.0f%%  R %3.0f G %3.0f B %3.0f'
          % (y0, y1, 100.0 * sel.mean(), c[0], c[1], c[2]))
