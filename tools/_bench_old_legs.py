# -*- coding: utf-8 -*-
"""Карта низа у СТАРОЙ скамейки: какие ножки реально доходят до земли.

Нужно понять, какую ножку дорисовывать и какой кусок брать за образец.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')
a = np.asarray(Image.open(P).convert('RGBA'))
m = a[:, :, 3] > 140
Hf, Wf = m.shape
print('файл %dx%d' % (Wf, Hf))

x0, x1, y0, y1 = 430, 720, 700, 986
sub = m[y0:y1, x0:x1]
cols, rows = 72, 36
bx, by = sub.shape[1] / cols, sub.shape[0] / rows
print('область x %d..%d, y %d..%d (ближняя ПЕРЕДНЯЯ ножка)' % (x0, x1, y0, y1))
print('     ' + ''.join(str((i // 10) % 10) for i in range(cols)))
for j in range(rows):
    yy0, yy1 = int(j * by), max(int(j * by) + 1, int((j + 1) * by))
    row = ''
    for i in range(cols):
        xx0, xx1 = int(i * bx), max(int(i * bx) + 1, int((i + 1) * bx))
        v = sub[yy0:yy1, xx0:xx1].mean()
        row += '#' if v > 0.75 else ('+' if v > 0.4 else ('.' if v > 0.12 else ' '))
    print('%4d %s' % (y0 + int(j * by), row))

print('\nто же для правого конца (где должна быть ДАЛЬНЯЯ ПЕРЕДНЯЯ ножка):')
x0, x1, y0, y1 = 1080, 1303, 330, 720
sub = m[y0:y1, x0:x1]
cols, rows = 56, 40
bx, by = sub.shape[1] / cols, sub.shape[0] / rows
print('     ' + ''.join(str((i // 10) % 10) for i in range(cols)))
for j in range(rows):
    yy0, yy1 = int(j * by), max(int(j * by) + 1, int((j + 1) * by))
    row = ''
    for i in range(cols):
        xx0, xx1 = int(i * bx), max(int(i * bx) + 1, int((i + 1) * bx))
        v = sub[yy0:yy1, xx0:xx1].mean()
        row += '#' if v > 0.75 else ('+' if v > 0.4 else ('.' if v > 0.12 else ' '))
    print('%4d %s' % (y0 + int(j * by), row))
