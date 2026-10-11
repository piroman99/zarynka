# -*- coding: utf-8 -*-
"""Проверка: реально ли рисуется гравировка на ребре (по пикселям цвета штампа)."""
import os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, '_intro_k2b.py')).read().split("if '--sheet' in sys.argv:")[0]
ns = {'__file__': os.path.join(HERE, '_intro_k2b.py'), '__name__': 'k2bmod'}
exec(compile(src, '_intro_k2b.py', 'exec'), ns)
render = ns['render']
for tt in (2.10, 2.25, 2.45, 2.60, 2.75):
    a = np.asarray(render(int(tt * 25))).astype(int)
    # зона центральной вертикальной полосы
    band = a[:, 890:1030, :]
    r, g, b = band[:, :, 0], band[:, :, 1], band[:, :, 2]
    dark = ((r > 70) & (r < 150) & (g > 50) & (g < 120) & (b > 10) & (b < 90)).sum()
    bright = ((r > 200) & (g > 180)).sum()
    print('t=%.2f  тёмн.пикс(гравировка)=%6d  светл.пикс(металл)=%6d' % (tt, dark, bright))
