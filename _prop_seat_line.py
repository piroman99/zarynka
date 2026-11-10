# -*- coding: utf-8 -*-
"""Сильные ГОРИЗОНТАЛЬНЫЕ кромки в пропе-скамейке: где спинка, где передняя кромка сиденья.

Считаем по строкам сумму |dY| (вертикальный градиент яркости) внутри маски, отдельно для
ближней трети (x 5..35 %) и для всей скамейки. Две самые сильные линии в верхней половине —
рейки спинки, в нижней — передняя кромка сиденья и край сиденья у спинки.
Печатаем топ-строки и производные доли: (земля − сиденье) / (земля − верх спинки).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'assets', 'sprites', 'prop_bench.png')
im = Image.open(P).convert('RGBA')
rgb = np.asarray(im.convert('RGB')).astype(np.float32)
a = np.asarray(im.split()[-1]).astype(np.float32) / 255.0
lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
h, w = lum.shape

gy = np.zeros_like(lum)
gy[1:-1] = np.abs(lum[2:] - lum[:-2]) * 0.5
gy *= a                     # только внутри фигуры

ys, xs = np.nonzero(a > 0.55)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print('маска x %d..%d y %d..%d (%dx%d)' % (x0, x1, y0, y1, w, h))


def profile(xa, xb, label):
    sub = gy[:, int(x0 + xa * (x1 - x0)):int(x0 + xb * (x1 - x0))]
    prof = sub.sum(1)
    # сглаживаем по 3 строки, чтобы не ловить одиночный шум
    k = np.array([0.25, 0.5, 0.25])
    prof = np.convolve(prof, k, mode='same')
    order = np.argsort(prof)[::-1]
    picked = []
    for y in order:
        if y < y0 + 2 or y > y1 - 2:
            continue
        if all(abs(y - p) > 12 for p in picked):
            picked.append(int(y))
        if len(picked) >= 8:
            break
    print('\n--- %s (x %.0f..%.0f%% длины) ---' % (label, 100 * xa, 100 * xb))
    for y in sorted(picked):
        print('   y %4d  (%.1f%% высоты маски)  сила %6.1f' % (y, 100.0 * (y - y0) / (y1 - y0),
                                                               prof[y]))
    return prof, picked


prof_near, near = profile(0.05, 0.35, 'ближняя треть')
prof_all, all_ = profile(0.0, 1.0, 'вся скамейка')

# земля у ближнего торца: низ маски в полосе 5..20 %
band = a[:, int(x0 + 0.05 * (x1 - x0)):int(x0 + 0.20 * (x1 - x0))] > 0.55
rows = np.nonzero(band.any(1))[0]
ground = rows.max()
print('\nземля у ближнего торца: y=%d' % ground)
print('верх маски в этой полосе: y=%d' % rows.min())

# ищем нижнюю сильную кромку (сиденье) и верхнюю (спинка)
lower = [y for y in near if y > ground - 0.60 * (ground - rows.min())]
upper = [y for y in near if y < ground - 0.60 * (ground - rows.min())]
print('\nкандидаты «сиденье» (нижние 40 %% высоты): %s' % lower)
print('кандидаты «спинка» (верхние 60 %%): %s' % upper)
for y in lower:
    print('   если сиденье y=%d -> (земля-сиденье)/(земля-верх) = %.3f'
          % (y, (ground - y) / float(ground - rows.min())))
