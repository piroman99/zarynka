# -*- coding: utf-8 -*-
"""Маска различий слоя на кадре 12 в полосе чипа: on vs off, только участок чипа.
Показывает реальные границы плашки и текста в 2400-пространстве."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
E = 2400.0
A = Image.open(os.path.join(HERE, '_sat', 's5b_on.png')).convert('RGB')
B = Image.open(os.path.join(HERE, '_sat', 's5b_off.png')).convert('RGB')
W, H = A.size
k = W / E
pa, pb = A.load(), B.load()

x0, x1 = int(400 * k), int(1600 * k)
y0, y1 = int(780 * k), int(960 * k)
mask = Image.new('L', (x1 - x0, y1 - y0), 0)
mp = mask.load()
cols = {}
for y in range(y0, y1):
    for x in range(x0, x1):
        ra, ga, ba = pa[x, y]
        rb, gb, bb = pb[x, y]
        if abs(ra - rb) + abs(ga - gb) + abs(ba - bb) > 40:
            mp[x - x0, y - y0] = 255
            cols[x] = cols.get(x, 0) + 1
mask = mask.resize(((x1 - x0) * 2, (y1 - y0) * 2), Image.NEAREST)
o = os.path.join(HERE, '_sat', 's5b_mask.png')
mask.save(o)
print('saved', os.path.relpath(o, HERE), mask.size)
if cols:
    xs = sorted(cols)
    print('различия по x: %4.0f..%4.0f (в 2400)' % (xs[0] * k, xs[-1] * k))
    # плотность: где текст (много пикселей) и где только плашка (мало)
    dense = [x for x in xs if cols[x] > 12]
    if dense:
        print('плотные столбцы (буквы): %4.0f..%4.0f' % (min(dense) * k, max(dense) * k))
