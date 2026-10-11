# -*- coding: utf-8 -*-
"""Численная проверка геометрии призмы по углам (без глаз)."""
import os, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_znak3d.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_znak3d.py'), '__name__': 'z3d'}
exec(compile(src, '_znak3d.py', 'exec'), ns)
render = ns['render']
BG = 12  # фон ~ (6,8,18)
for a in (0, 18, 36, 54, 72, 90):
    im = np.asarray(render(a)).astype(int)
    fg = (np.abs(im - np.array([6, 8, 18])).sum(axis=2) > 24)
    cols = np.where(fg.any(axis=0))[0]
    rows = np.where(fg.any(axis=1))[0]
    wpx = (cols.max() - cols.min() + 1) if len(cols) else 0
    hpx = (rows.max() - rows.min() + 1) if len(rows) else 0
    print('%3d°  ширина силуэта=%4d px  высота=%4d px  площадь=%6d' % (a, wpx, hpx, int(fg.sum())))
