# -*- coding: utf-8 -*-
"""Диагностика кромки спрайта: есть ли светлая кайма (halo) по краю альфы.

Меряем:
  * распределение альфы (сколько пикселей полупрозрачных);
  * среднюю яркость в кольцах от края внутрь;
  * сколько пикселей у края светлее ядра более чем на 25 по яркости.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
NAME = sys.argv[1] if len(sys.argv) > 1 else 'poet_seat_upset.webp'
P = os.path.join(ROOT, 'vn2', 'img', 'char', NAME)

im = Image.open(P).convert('RGBA')
a = np.asarray(im).astype(float)
rgb, al = a[:, :, :3], a[:, :, 3]
h, w = al.shape
print('%s %dx%d' % (NAME, w, h))

tot = (al > 0).sum()
print('пикселей с альфой >0: %d, >0.9: %d, 0.1..0.5: %d'
      % (tot, (al > 230).sum(), ((al > 25) & (al <= 128)).sum()))

lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
body = al > 230
core_lum = lum[body].mean()
print('средняя яркость плотного ядра: %.1f' % core_lum)

# кольца от края: эрозия альфы
def erode(mask, n=1):
    m = mask.copy()
    for _ in range(n):
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        m = e
    return m

solid = al > 128
edge = solid & ~erode(solid, 2)
print('\nкромка (полоса 2 px внутри плотной зоны): %d px' % edge.sum())
print('  яркость кромки %.1f, ядра %.1f (разница %+.1f)'
      % (lum[edge].mean(), core_lum, lum[edge].mean() - core_lum))

inner = solid & ~erode(solid, 8)
print('  яркость слоя 2..8 px от края %.1f' % lum[edge & ~inner].mean() if (edge & ~inner).any() else '')

# светлые пиксели у края
light_edge = edge & (lum > core_lum + 25)
print('  светлее ядра на 25+: %d px (%.1f%% кромки)'
      % (light_edge.sum(), 100.0 * light_edge.sum() / max(1, edge.sum())))

# полупрозрачная «бахрома»
fringe = (al > 20) & (al <= 180)
if fringe.any():
    print('  полупрозрачная бахрома: %d px, яркость %.1f'
          % (fringe.sum(), lum[fringe].mean()))

# яркостный профиль по кольцам
print('\nпрофиль яркости по глубине от края:')
for d in range(0, 9):
    ring = solid & erode(solid, d) & ~erode(solid, d + 1)
    if ring.any():
        print('  глубина %d px: пикселей %6d, яркость %6.1f, альфа %5.1f'
              % (d, ring.sum(), lum[ring].mean(), al[ring].mean()))
