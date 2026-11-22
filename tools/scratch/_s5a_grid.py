# -*- coding: utf-8 -*-
"""Кроп стенда в A: подобрать точные границы под полосу лозунга."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
GEN = os.path.join(ROOT, 'assets', 'gen')
OUT = os.path.join(ROOT, '_sat')
im = Image.open(os.path.join(GEN, 's5a_a__gpt-image-2_0.png')).convert('RGB')
w, h = im.size
# сетка 5% с подписями долей — чтобы точно снять границы стенда
g = im.copy()
d = ImageDraw.Draw(g)
for f in range(1, 20):
    x = int(w * f / 20)
    d.line([(x, 0), (x, h)], fill=(255, 0, 0), width=1)
    d.text((x + 2, 4), '%d' % (f * 5), fill=(255, 255, 0))
for f in range(1, 20):
    y = int(h * f / 20)
    d.line([(0, y), (w, y)], fill=(255, 0, 0), width=1)
    d.text((2, y + 1), '%d' % (f * 5), fill=(255, 255, 0))
p = os.path.join(OUT, 's5a_a_grid.png')
g.save(p)
print('saved', p, g.size)
