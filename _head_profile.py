# -*- coding: utf-8 -*-
"""Ширина фигуры по строкам (2 % шага): где у Екатерины голова, где плечи, и какого
размера голова у сидящего поэта. Нужно, чтобы сравнить их «в одном кадре»."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def profile(path, label):
    im = Image.open(path).convert('RGBA')
    a = np.asarray(im.split()[-1])
    m = a > 128
    ys, xs = np.nonzero(m)
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0 + 1
    print('\n=== %s %dx%d, фигура %d px (%.3f холста) ===' % (label, im.width, im.height,
                                                             bh, bh / im.height))
    print('  %5s %7s %8s' % ('y%', 'ширина', 'px'))
    for k in range(0, 51):
        y = y0 + int(bh * k / 50.0)
        y = min(y, y1)
        cols = np.nonzero(m[y])[0]
        w = (cols.max() - cols.min()) if len(cols) else 0
        print('  %5.0f %7.0f%% %8d' % (100.0 * k / 50.0, 100.0 * w / im.width, w))


profile(os.path.join(HERE, 'vn2', 'img', 'char', 'kate.webp'), 'Екатерина (стоит)')
profile(os.path.join(HERE, 'assets', 'sprites', 'poet_seat_neutral.png'), 'Поэт (сидит)')
