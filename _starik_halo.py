# -*- coding: utf-8 -*-
"""Ореол по кромке: смотрим ТОЛЬКО нижнюю треть (пиджак, тёмный) — там серый фон сразу виден.
Для каждой строки находим левую/правую кромку силуэта и берём 3 внешних px (alpha>0)
+ 2 внутренних: если снаружи светло-серое (L>170) — ореол.
"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets', 'sprites', 'starik_stern.png')).convert('RGBA')
px = im.load()
w, h = im.size
y0, y1 = int(h * 0.62), int(h * 0.97)
out_l = []
out_r = []
for y in range(y0, y1, 4):
    xs = [x for x in range(w) if px[x, y][3] > 10]
    if not xs:
        continue
    for x in xs[:3]:
        r, g, b, a = px[x, y]
        out_l.append((0.299 * r + 0.587 * g + 0.114 * b, a))
    for x in xs[-3:]:
        r, g, b, a = px[x, y]
        out_r.append((0.299 * r + 0.587 * g + 0.114 * b, a))
allb = out_l + out_r
n = len(allb)
light = sum(1 for L, a in allb if L > 170)
semi = sum(1 for L, a in allb if 60 < a < 200)
print('band px', n, '| светлых (L>170) %.1f%%' % (100.0 * light / n),
      '| полупрозрачных %.1f%%' % (100.0 * semi / n),
      '| средняя L %.0f' % (sum(L for L, _ in allb) / n))
