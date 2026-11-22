# -*- coding: utf-8 -*-
"""Проверка диагностического рендера: где на экране планка (красная) перекрывает стойку
(синюю) — значит планка ближе к зрителю, то есть прибита с внутренней стороны."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'blend', 'diag.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im).astype(int)
h, w = a.shape[:2]
rgb = a[:, :, :3]
al = a[:, :, 3] > 128

red = al & (rgb[:, :, 0] > 120) & (rgb[:, :, 1] < 90) & (rgb[:, :, 2] < 90)
blue = al & (rgb[:, :, 2] > 120) & (rgb[:, :, 0] < 90) & (rgb[:, :, 1] < 110)
print('файл %dx%d  красных %d, синих %d' % (w, h, red.sum(), blue.sum()))

# область стоек: ищем синие вертикальные полосы, у которых выше по экрану идёт красное
cols = np.nonzero(blue.any(axis=0))[0]
print('синие колонки: %d..%d' % (cols.min(), cols.max()))

# для каждой синей колонки смотрим, есть ли красное ПЕРЕД ней по той же колонке
# (планка наезжает на стойку => в этой колонке сверху/снизу красное)
overlap_cols = 0
for x in cols:
    col_b = np.nonzero(blue[:, x])[0]
    col_r = np.nonzero(red[:, x])[0]
    if col_b.size and col_r.size:
        # пересекаются ли диапазоны по y (в проекции)
        if col_r.min() <= col_b.max() and col_b.min() <= col_r.max():
            overlap_cols += 1
print('колонок, где красное и синее накладываются по y: %d из %d (%.0f%%)'
      % (overlap_cols, len(cols), 100.0 * overlap_cols / max(1, len(cols))))

# главное: в спорной зоне стоек, что стоит в пикселе — красное или синее?
# берём полосу между планками и стойками на ближнем торце
x0, x1 = int(w * 0.10), int(w * 0.30)
y0, y1 = int(h * 0.10), int(h * 0.75)
zone_b = blue[y0:y1, x0:x1]
zone_r = red[y0:y1, x0:x1]
print('\nзона ближней стойки x[%d..%d] y[%d..%d]: синих %d, красных %d'
      % (x0, x1, y0, y1, zone_b.sum(), zone_r.sum()))

# профиль по горизонтали на высоте середины спинки: где кончается красное и начинается синее
ymid = int(h * 0.40)
row_b = np.nonzero(blue[ymid, :])[0]
row_r = np.nonzero(red[ymid, :])[0]
print('строка y=%d: синие x %s, красные x %s'
      % (ymid,
         ('нет' if not row_b.size else '%d..%d' % (row_b.min(), row_b.max())),
         ('нет' if not row_r.size else '%d..%d' % (row_r.min(), row_r.max()))))
