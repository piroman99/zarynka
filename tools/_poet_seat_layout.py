# -*- coding: utf-8 -*-
"""Где фигура внутри холста сидячего спрайта (верх/низ поля) и сколько места ей нужно.

Нужно, чтобы понять: если увеличить поэта на 40 %, не уедет ли макушка за верх сцены
и где окажутся ступни относительно земли.
"""
import os
import glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SPR = os.path.join(ROOT, 'assets', 'sprites')

print('%-26s %9s %11s %7s %7s %7s' % ('спрайт', 'холст', 'фигура y', 'верх %', 'низ %', 'доля'))
for f in sorted(glob.glob(os.path.join(SPR, 'poet_seat_*.png'))):
    a = np.asarray(Image.open(f).split()[-1]).astype(np.float32)
    m = a > 60
    ys, xs = np.nonzero(m)
    ch, cw = a.shape
    y0, y1 = ys.min(), ys.max()
    print('%-26s %9s %11s %6.1f%% %6.1f%% %6.1f%%'
          % (os.path.basename(f), '%dx%d' % (cw, ch), '%d..%d' % (y0, y1),
             100.0 * y0 / ch, 100.0 * (ch - 1 - y1) / ch, 100.0 * (y1 - y0 + 1) / ch))

# Кейт для масштаба: её фигура в спрайте и рост 1.70 м
for name in ('kate', 'poet', 'sergey'):
    p = os.path.join(ROOT, 'vn2', 'img', 'char', name + '.webp')
    if not os.path.exists(p):
        continue
    im = Image.open(p)
    a = np.asarray(im.split()[-1]).astype(np.float32)
    m = a > 60
    ys, xs = np.nonzero(m)
    ch, cw = a.shape
    print('\n%-10s холст %dx%d  фигура %dx%d  верх %.1f%% низ %.1f%%  доля H %.1f%%'
          % (name, cw, ch, xs.max() - xs.min() + 1, ys.max() - ys.min() + 1,
             100.0 * ys.min() / ch, 100.0 * (ch - 1 - ys.max()) / ch,
             100.0 * (ys.max() - ys.min() + 1) / ch))
