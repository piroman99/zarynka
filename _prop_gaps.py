# -*- coding: utf-8 -*-
"""Просветы (прозрачные щели) внутри силуэта пропа: где доска сиденья кончается.

Для колонок ближней половины печатаем все щели между полосами дерева: положение, высоту.
Самая большая щель в нижней половине — это просвет ПОД сиденьем (между сиденьем и землёй),
её верх = низ доски сиденья. Так сиденье находится без «на глаз».
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets', 'sprites', 'prop_bench.png')).convert('RGBA')
a = np.asarray(im.split()[-1])
m = a > 140
h, w = m.shape
ys, xs = np.nonzero(m)
x0, x1 = xs.min(), xs.max()


def runs(x):
    col = m[:, x]
    idx = np.nonzero(np.diff(np.concatenate(([0], col.view(np.int8), [0]))))[0]
    return [(int(idx[i]), int(idx[i + 1]) - 1) for i in range(0, len(idx), 2)]


print('%5s %5s | %s' % ('x', 'x%', 'полосы дерева'))
for frac in (0.08, 0.12, 0.16, 0.20, 0.24, 0.28, 0.32, 0.38, 0.45, 0.55, 0.65):
    x = int(x0 + frac * (x1 - x0))
    r = runs(x)
    txt = '  '.join('%d-%d(%d)' % (ya, yb, yb - ya + 1) for ya, yb in r)
    print('%5d %4.0f%% | %s' % (x, 100 * frac, txt))

print('\nсамая большая щель в нижней половине каждой колонки (между 45% и 100% высоты):')
tops, bots = ys.min(), ys.max()
for frac in np.arange(0.06, 0.60, 0.04):
    x = int(x0 + frac * (x1 - x0))
    r = runs(x)
    if len(r) < 2:
        continue
    gaps = []
    for i in range(len(r) - 1):
        ga, gb = r[i][1] + 1, r[i + 1][0] - 1
        if ga > bots - 0.60 * (bots - tops):
            gaps.append((gb - ga + 1, ga, gb))
    if not gaps:
        continue
    g = max(gaps)
    print('  x=%4d (%3.0f%% длины): щель y %d..%d (%d px), над ней дерево до y=%d, '
          'под ней с y=%d' % (x, 100 * frac, g[1], g[2], g[0], g[1] - 1, g[2] + 1))
