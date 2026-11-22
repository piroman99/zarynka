# -*- coding: utf-8 -*-
"""Геометрия пропа-скамейки: под каким углом она стоит и где линии сиденья.

Считаем по альфе (плотное дерево, a>90):
  • PCA плотных пикселей → длинная ось скамейки (угол к горизонту);
  • профиль по колонкам: верхняя кромка спинки → наклон (линейная подгонка);
  • профиль по строкам: покрытие → где сиденье (резкий спад под передней кромкой).
Печатаем числа, чтобы не судить «на глаз».
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
p = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
im = Image.open(p)
print('проп:', im.mode, im.size)
a = np.asarray(im.split()[-1]).astype(np.float32)
H, W = a.shape
m = a > 90
ys, xs = np.nonzero(m)
print('плотных пикселей: %d (%.1f%% кадра)' % (len(xs), 100.0 * len(xs) / (H * W)))
print('bbox: x %d..%d  y %d..%d  (%dx%d)' % (xs.min(), xs.max(), ys.min(), ys.max(),
                                              xs.max() - xs.min(), ys.max() - ys.min()))

# --- PCA длинной оси ---
pts = np.stack([xs.astype(np.float64), ys.astype(np.float64)], 1)
c = pts.mean(0)
cov = np.cov((pts - c).T)
w, v = np.linalg.eigh(cov)
main = v[:, np.argmax(w)]
ang = np.degrees(np.arctan2(main[1], main[0]))
if ang > 90:
    ang -= 180
if ang < -90:
    ang += 180
print('PCA длинная ось: %.2f° к горизонту (положительный = правый край НИЖЕ)' % ang)
print('  разброс по осям: %.1f / %.1f px (отношение %.2f)'
      % (np.sqrt(w.max()), np.sqrt(w.min()), np.sqrt(w.max() / w.min())))

# --- верхняя кромка (спинка) по колонкам ---
cols = np.arange(W)
top = np.full(W, np.nan)
for x in range(W):
    col = np.nonzero(m[:, x])[0]
    if col.size:
        top[x] = col.min()
valid = ~np.isnan(top)
x0, x1 = xs.min(), xs.max()
span = x1 - x0
# центральные 50 % ширины: там кромка спинки без «перьев» и без растушёвки
lo = int(x0 + 0.25 * span)
hi = int(x0 + 0.75 * span)
sel = valid & (cols >= lo) & (cols <= hi)
k, b = np.polyfit(cols[sel], top[sel], 1)
print('верхняя кромка (центр 50%% ширины, x %d..%d): наклон %.4f → %.2f°'
      % (lo, hi, k, np.degrees(np.arctan(k))))
print('  y на левом/правом краю выборки: %.0f / %.0f' % (k * lo + b, k * hi + b))

# --- покрытие по строкам: где сиденье ---
cov_rows = m.sum(1)
peak = cov_rows.max()
print('макс. покрытие строки: %d px (строка %d)' % (peak, int(np.argmax(cov_rows))))
# ищем самый резкий спад покрытия НИЖЕ строки максимума
below = cov_rows[int(np.argmax(cov_rows)):]
drops = np.diff(below.astype(np.int32))
i = int(np.argmin(drops))
seat_edge = int(np.argmax(cov_rows)) + i
print('резкий спад под сиденьем: строка %d (дельта %d px)' % (seat_edge, drops[i]))
# профиль для чтения
print('\nпрофиль покрытия (каждая 5%% высоты):')
for f in range(0, 21):
    y = min(H - 1, int(f / 20.0 * H))
    print('  y=%4d (%2d%%): %5d px %s' % (y, f * 5, cov_rows[y],
                                          '#' * int(60 * cov_rows[y] / peak)))
