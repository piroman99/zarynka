# -*- coding: utf-8 -*-
"""Разбор НОВОЙ скамейки (assets/gen/bench2_0.png) без зрения: разворот, торцы, сиденье.

Что печатаем:
  1) bbox «дерева» и касается ли он краёв кадра (значит генератор обрезал);
  2) PCA длинной оси маски -> угол наклона скамейки в кадре;
  3) по колонкам верх/низ маски -> где ближний торец (высокая колонка) и где дальний;
  4) профиль заполнения по строкам -> где полоса сиденья и где просвет под ним;
  5) ASCII силуэта в полном разрешении (плотная маска).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _poet_matte import matte  # noqa: E402

P = os.path.join(HERE, 'assets', 'gen', 'bench2_0.png')

rgba, st = matte(Image.open(P))
a = np.asarray(rgba.split()[-1]).astype(np.float32)
m = a > 140
print('%s %dx%d, плотных пикселей %.1f%%, фон снят %.0f%%'
      % (os.path.basename(P), rgba.width, rgba.height, 100 * m.mean(), 100 * st['removed']))

ys, xs = np.nonzero(m)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print('bbox: x %d..%d  y %d..%d  (%dx%d)'
      % (x0, x1, y0, y1, x1 - x0 + 1, y1 - y0 + 1))
for side, val, lim in (('левый', x0, 3), ('правый', rgba.width - 1 - x1, 3),
                       ('верхний', y0, 3), ('нижний', rgba.height - 1 - y1, 3)):
    print('  %-8s край: %d px до рамки%s' % (side, val, '  <-- ОБРЕЗАНО' if val <= lim else ''))

# PCA длинной оси
pts = np.stack([xs, ys], 1).astype(np.float64)
c = pts.mean(0)
cov = np.cov((pts - c).T)
w, v = np.linalg.eigh(cov)
main = v[:, np.argmax(w)]
ang = np.degrees(np.arctan2(main[1], main[0]))
if ang > 90:
    ang -= 180
if ang < -90:
    ang += 180
print('PCA длинной оси: %.1f° (0 = горизонтально, минус = вверх-вправо), '
      'отношение осей %.2f' % (ang, (max(w) / max(min(w), 1e-9)) ** 0.5))

# профиль по колонкам: верх и низ
prof = []
for x in range(x0, x1 + 1):
    col = np.nonzero(m[:, x])[0]
    if len(col):
        prof.append((x, col.min(), col.max(), col.max() - col.min() + 1))
prof = np.array(prof, float)
print('\nвысота скамейки по колонкам (каждая 1/10 ширины):')
for k in range(10):
    i = int((len(prof) - 1) * k / 9)
    print('  x %4.0f (%3.0f%%)  верх %4.0f  низ %4.0f  высота %4.0f'
          % (prof[i, 0], 100 * (prof[i, 0] - x0) / (x1 - x0), prof[i, 1], prof[i, 2], prof[i, 3]))
i_max = int(np.argmax(prof[:, 3]))
print('самая высокая колонка: x=%.0f высота %.0f px -> %s торец'
      % (prof[i_max, 0], prof[i_max, 3],
         'ЛЕВЫЙ' if prof[i_max, 0] < (x0 + x1) / 2 else 'ПРАВЫЙ'))

# верхняя кромка (спинка) — наклон
sel = prof[(prof[:, 0] > x0 + 0.08 * (x1 - x0)) & (prof[:, 0] < x1 - 0.08 * (x1 - x0))]
if len(sel) > 20:
    k1, b1 = np.polyfit(sel[:, 0], sel[:, 1], 1)
    print('верхняя кромка: наклон %.1f° (плюс = вниз-вправо)' % np.degrees(np.arctan(k1)))

# профиль заполнения по строкам
print('\nзаполнение по строкам (24 полосы, % ширины в каждой):')
for r in range(24):
    yy = int(y0 + (y1 - y0) * r / 24)
    row = m[yy]
    cols = np.nonzero(row)[0]
    print('  y %4d (%3.0f%%)  заполнено %5.1f%%  x %4.0f..%4.0f'
          % (yy, 100 * (yy - y0) / max(1, y1 - y0), 100 * row.mean(),
             cols.min() if len(cols) else 0, cols.max() if len(cols) else 0))

# ASCII
cols_n, rows_n = 96, 32
print('\nсилуэт:')
for r in range(rows_n):
    ya, yb = y0 + int((y1 - y0) * r / rows_n), y0 + int((y1 - y0) * (r + 1) / rows_n)
    line = []
    for cc in range(cols_n):
        xa = x0 + int((x1 - x0) * cc / cols_n)
        xb = x0 + int((x1 - x0) * (cc + 1) / cols_n)
        f = m[ya:max(yb, ya + 1), xa:max(xb, xa + 1)].mean()
        line.append('#' if f > 0.6 else ('+' if f > 0.25 else ('.' if f > 0.06 else ' ')))
    print('|' + ''.join(line) + '|')
