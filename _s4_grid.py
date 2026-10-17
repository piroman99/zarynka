# -*- coding: utf-8 -*-
"""Сетка на финальном кадре S4 — чтобы точно увидеть границы телевизора и подписи."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
src = Image.open(os.path.join(HERE, 'assets/final/prolog/s4.png')).convert('RGB')
W, H = src.size
im = src.copy()
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 22)
for x in range(0, W, 100):
    col = (0, 255, 0) if x % 500 == 0 else (0, 140, 0)
    d.line([(x, 0), (x, H)], fill=col, width=2 if x % 500 == 0 else 1)
    d.text((x + 3, 4), str(x), font=f, fill=(0, 255, 0))
for y in range(0, H, 100):
    col = (255, 220, 0) if y % 500 == 0 else (140, 120, 0)
    d.line([(0, y), (W, y)], fill=col, width=2 if y % 500 == 0 else 1)
    d.text((4, y + 2), str(y), font=f, fill=(255, 220, 0))
out = os.path.join(REV, '_s4_grid.png')
im.save(out)
print(out, im.size)

# то же в пространстве сборки 2400x1350
im2 = im.resize((2400, 1350), Image.LANCZOS)
d2 = ImageDraw.Draw(im2)
for x in range(0, 2400, 100):
    d2.line([(x, 0), (x, 1350)], fill=(0, 90, 255), width=1)
for y in range(0, 1350, 100):
    d2.line([(0, y), (2400, y)], fill=(0, 60, 180), width=1)
im2.resize((1200, 675), Image.LANCZOS).save(os.path.join(REV, '_s4_grid24.png'))
print('2400-сетка: _s4_grid24.png')
