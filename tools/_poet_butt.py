# -*- coding: utf-8 -*-
"""Где у спрайта низ задней части тела (то, чем сидят) и где ступни.

Профиль НИЗА силуэта по колонкам: сзади (под тазом/бёдрами) низ резко уходит
вверх — это и есть линия контакта с доской; спереди низ идёт до ступней.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)[:, :, 3] > 100
h, w = a.shape
print('спрайт %dx%d' % (w, h))

bot = np.full(w, h)
top = np.full(w, 0)
for x in range(w):
    idx = np.nonzero(a[:, x])[0]
    if idx.size:
        bot[x] = idx.max()
        top[x] = idx.min()

print('\nниз силуэта по колонкам (шаг 4%%):')
for c in range(0, 101, 4):
    x = min(int(w * c / 100.0), w - 1)
    if bot[x] < h:
        print('  %3d%% x=%4d  верх %4d  низ %4d (%.3f)' % (c, x, top[x], bot[x], bot[x] / h))

# «полка» — самая высокая зона низа в задней половине
rear = bot[: w // 2]
front = bot[w // 2:]
print('\nзадняя половина: низ мин %d (%.3f), макс %d (%.3f)'
      % (rear.min(), rear.min() / h, rear.max(), rear.max() / h))
print('передняя половина: низ мин %d (%.3f), макс %d (%.3f)'
      % (front.min(), front.min() / h, front.max(), front.max() / h))

# ищем плоскую полку: самый частый уровень низа в задней половине
vals, counts = np.unique(rear[rear < h], return_counts=True)
order = np.argsort(-counts)[:6]
print('\nсамые частые уровни низа в задней половине:')
for i in order:
    print('  y=%4d (%.3f)  колонок %d' % (vals[i], vals[i] / h, counts[i]))

# ASCII нижней половины
print('\nнижняя половина (строка = 1%, столбец = 1.5%):')
for pct in range(50, 101, 1):
    y = min(h - 1, int(h * pct / 100.0))
    line = []
    for c in range(0, 100, 1):
        x0 = int(w * c / 100.0)
        x1 = max(int(w * (c + 1) / 100.0), x0 + 1)
        d = a[y, x0:x1].mean()
        line.append('#' if d > 0.5 else ('+' if d > 0.15 else ' '))
    print('%3d%%|%s' % (pct, ''.join(line)))
