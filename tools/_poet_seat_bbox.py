# -*- coding: utf-8 -*-
"""Что реально занимает сидячий спрайт поэта: bbox фигуры внутри холста.

Движок ставит `.sprite.seated{height:75%}` — то есть 75 % высоты СЦЕНЫ на ВЕСЬ ХОЛСТ,
включая прозрачные поля. Если поля большие и у разных эмоций разные, фигура в кадре
получается мелкой и «прыгает» по размеру от эмоции к эмоции.
"""
import os
import glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SPR = os.path.join(ROOT, 'assets', 'sprites')
files = sorted(glob.glob(os.path.join(SPR, 'poet_seat_*.png')))

print('%-28s %10s %10s %7s %7s %8s %8s' % ('файл', 'холст', 'фигура', 'доля H', 'доля W',
                                           'голова', 'h/w фиг.'))
rows = []
for f in files:
    im = Image.open(f)
    a = np.asarray(im.split()[-1]).astype(np.float32)
    m = a > 60
    ys, xs = np.nonzero(m)
    ch, cw = a.shape
    fh, fw = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
    # ширина головы: в верхних 12 % фигуры берём ширину по строкам и берём минимум
    top = ys.min()
    band = m[top:top + max(4, int(fh * 0.12))]
    widths = [np.count_nonzero(row) for row in band if row.any()]
    head_w = int(np.median(widths)) if widths else 0
    rows.append((os.path.basename(f), cw, ch, fw, fh, head_w))
    print('%-28s %10s %10s %6.1f%% %6.1f%% %8d %8.2f'
          % (os.path.basename(f), '%dx%d' % (cw, ch), '%dx%d' % (fw, fh),
             100.0 * fh / ch, 100.0 * fw / cw, head_w, fh / float(fw)))

hs = [r[4] / r[2] for r in rows]
print('\nдоля высоты холста, занятая фигурой: %.1f%% .. %.1f%% (разброс %.2f×)'
      % (100 * min(hs), 100 * max(hs), max(hs) / min(hs)))
print('если движок даёт холсту 75 %% сцены, фигура получает %.1f%% .. %.1f%% сцены'
      % (75 * min(hs), 75 * max(hs)))
