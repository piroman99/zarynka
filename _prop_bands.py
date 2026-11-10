# -*- coding: utf-8 -*-
"""Где у новой скамейки РЕАЛЬНО сиденье: разбираем колонки на полосы по альфе.

Спинка = несколько реек, между ними и сиденьем просвет, ниже — сиденье (широкая доска),
ещё ниже — ножки (узкие). Печатаем полосы для колонок ближнего торца и середины,
чтобы взять линию сиденья из картинки, а не из «половины высоты».
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'assets', 'sprites', 'prop_bench.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im.split()[-1])
m = a > 140
h, w = m.shape
ys, xs = np.nonzero(m)
x0, x1 = xs.min(), xs.max()
print('проп %dx%d, маска x %d..%d y %d..%d' % (w, h, x0, x1, ys.min(), ys.max()))


def runs(x):
    col = m[:, x]
    idx = np.nonzero(np.diff(np.concatenate(([0], col.view(np.int8), [0]))))[0]
    out = []
    for i in range(0, len(idx), 2):
        out.append((int(idx[i]), int(idx[i + 1]) - 1))
    return out


for frac in (0.02, 0.05, 0.10, 0.15, 0.25, 0.35, 0.5, 0.65, 0.8, 0.92):
    x = int(x0 + frac * (x1 - x0))
    r = runs(x)
    print('\nx=%4d (%.0f%% длины), полосы:' % (x, 100 * frac))
    for (ya, yb) in r:
        print('   y %4d..%4d  высота %4d  %s'
              % (ya, yb, yb - ya + 1, 'толстая' if yb - ya > 40 else ''))
