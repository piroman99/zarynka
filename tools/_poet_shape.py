# -*- coding: utf-8 -*-
"""ASCII-карта силуэта поэта + контуры по строкам: где на самом деле таз.

Таз сидящей фигуры — это место, где задний контур перестаёт идти вниз
(спина) и начинается «полка» (бёдра вперёд) или обрыв вниз (задняя часть бедра).
Печатаем левую и правую границы силуэта по строкам, чтобы найти этот излом.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3]
h, w = a.shape
m = a > 100
print('спрайт %dx%d' % (w, h))

COLS, ROWS = 90, 46
print('\nкарта силуэта:')
for r in range(ROWS):
    y0 = int(h * r / ROWS)
    y1 = max(int(h * (r + 1) / ROWS), y0 + 1)
    line = []
    for c in range(COLS):
        x0 = int(w * c / COLS)
        x1 = max(int(w * (c + 1) / COLS), x0 + 1)
        d = m[y0:y1, x0:x1].mean()
        line.append('#' if d > 0.55 else ('+' if d > 0.2 else ('.' if d > 0.02 else ' ')))
    print('%4d|%s' % (y0, ''.join(line)))

print('\nграницы силуэта (%% файла, y, левая, правая, ширина):')
prev_l = prev_r = None
for pct in range(14, 100, 1):
    y = min(h - 1, int(h * pct / 100.0))
    idx = np.nonzero(m[y])[0]
    if not idx.size:
        continue
    l, r = int(idx.min()), int(idx.max())
    mark = ''
    if prev_l is not None:
        dl, dr = l - prev_l, r - prev_r
        if abs(dl) >= 6 or abs(dr) >= 6:
            mark = '  <== скачок L%+d R%+d' % (dl, dr)
    print('%3d%% %4d  L%4d R%4d  w%4d%s' % (pct, y, l, r, r - l + 1, mark))
    prev_l, prev_r = l, r
