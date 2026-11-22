# -*- coding: utf-8 -*-
"""ASCII-силуэт картинки: даёт мне понять позу/пропорции без глаз.

Печатает маску «фигура/фон» (по расстоянию до цвета фона в углах кадра) и профиль
ширины по строкам, чтобы видеть: голова, плечи, руки, бёдра, колени, ступни.
"""
import os
import sys

import numpy as np
from PIL import Image

COLS = int(os.environ.get('COLS', 56))


def show(path, cols=COLS):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im, np.float32)
    h, w, _ = a.shape
    # цвет фона — медиана рамки в 6 px
    b = 6
    edge = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3),
                           a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)])
    bg = np.median(edge, 0)
    d = np.sqrt(((a - bg) ** 2).sum(2))
    mask = d > 26
    rows = max(1, int(round(cols * h / w * 0.5)))
    ch, cw = h / rows, w / cols
    grid = np.zeros((rows, cols), np.float32)
    for ry in range(rows):
        for rx in range(cols):
            grid[ry, rx] = mask[int(ry * ch):int((ry + 1) * ch),
                                int(rx * cw):int((rx + 1) * cw)].mean()
    print('%s  %dx%d  bg=%s  покрытие %.1f%%'
          % (os.path.basename(path), w, h, bg.astype(int).tolist(), 100 * mask.mean()))
    print('    ' + ''.join(str((i // 10) % 10) for i in range(cols)))
    for i, r in enumerate(grid):
        print('%3d %s  %4.1f%%' % (i, ''.join('#' if v > .55 else ('+' if v > .18 else '.') for v in r),
                                   100 * r.mean()))
    # профиль ширины фигуры по строкам (в % ширины кадра)
    ys, xs = np.nonzero(mask)
    if len(ys):
        print('bbox x %d..%d  y %d..%d' % (xs.min(), xs.max(), ys.min(), ys.max()))
        for ry in range(0, rows, max(1, rows // 12)):
            row = mask[int(ry * ch):int((ry + 1) * ch)]
            c = np.nonzero(row.any(0))[0]
            if len(c):
                print('  y %3d%%  ширина %3.0f%%  x %3.0f%%..%3.0f%%'
                      % (100 * ry / rows, 100 * (c.max() - c.min()) / w,
                         100 * c.min() / w, 100 * c.max() / w))


for p in sys.argv[1:]:
    show(p)
    print()
