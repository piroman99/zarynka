# -*- coding: utf-8 -*-
"""Замер блендер-рендера скамейки: габариты, опоры, наклон оси, размеры файла."""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'blend', sys.argv[1] if len(sys.argv) > 1 else 'bench_raw.png')

im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
m = a > 140
ys, xs = np.nonzero(m)
print('file %dx%d  плотных %.2f%%  bbox x[%d..%d] y[%d..%d]  (%dx%d px)'
      % (w, h, 100.0 * m.mean(), xs.min(), xs.max(), ys.min(), ys.max(),
         xs.max() - xs.min() + 1, ys.max() - ys.min() + 1))

# низ маски по колонкам
bot = np.full(w, np.nan)
for x in range(w):
    idx = np.nonzero(m[:, x])[0]
    if idx.size:
        bot[x] = idx.max()
ok = ~np.isnan(bot)
print('\nниз по колонкам (каждые 5%%) :')
for c in range(0, 101, 5):
    x = min(int(w * c / 100.0), w - 1)
    print('  %3d%% x=%4d  низ %s' % (c, x, 'нет' if np.isnan(bot[x]) else '%d' % bot[x]))

# «ножки»: колонки, где низ маски близок к максимуму
filled = bot.copy()
filled[~ok] = np.interp(np.arange(w)[~ok], np.arange(w)[ok], bot[ok])
ybot = np.nanmax(filled)
thr = ybot - 0.03 * h
feet = filled > thr
runs = []
s = None
for x in range(w + 1):
    v = feet[x] if x < w else False
    if v and s is None:
        s = x
    elif not v and s is not None:
        if x - s >= 3:
            runs.append((s, x - 1))
        s = None
print('\n«ножки» (полосы, доходящие до низа): %d' % len(runs))
for s, e in runs:
    cx = (s + e) / 2.0
    print('  x %d..%d (центр %.0f = %.3f доли), низ %d' % (s, e, cx, cx / w, filled[int(cx)]))

if len(runs) >= 2:
    xs_c = [(s + e) / 2.0 for s, e in runs]
    ys_c = [filled[int(c)] for s, e in runs for c in [(s + e) / 2.0]]
    for i in range(len(runs) - 1):
        dx = xs_c[i + 1] - xs_c[i]
        dy = ys_c[i + 1] - ys_c[i]
        if abs(dx) > 2:
            ang = np.degrees(np.arctan2(-dy, dx))
            print('  наклон между опорами %d-%d: dx %.0f dy %.0f -> %.1f° (вверх-вправо)'
                  % (i, i + 1, dx, dy, ang))

# цвет
rgb = np.asarray(im)[:, :, :3].astype(float)
sel = m
print('\nсредний цвет по маске: R%.0f G%.0f B%.0f' % tuple(rgb[sel].mean(axis=0)))
