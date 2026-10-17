# -*- coding: utf-8 -*-
"""Сетка 100 px поверх плашки S6-B (в пространстве сборки 2400x1350) — выбрать место табло."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('RGB')
im = im.resize((2400, 1350), Image.LANCZOS)
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 18)
for x in range(0, 2400, 100):
    d.line([(x, 0), (x, 1350)], fill=(255, 0, 0) if x % 500 == 0 else (255, 120, 120), width=1)
    if x % 200 == 0:
        d.text((x + 3, 4), str(x), font=f, fill=(255, 255, 0))
for y in range(0, 1350, 100):
    d.line([(0, y), (2400, y)], fill=(0, 200, 255) if y % 500 == 0 else (120, 220, 255), width=1)
    if y % 200 == 0:
        d.text((4, y + 2), str(y), font=f, fill=(255, 255, 0))
p = os.path.join(HERE, 'assets', 'review', '_s6_grid.png')
im.save(p)
print(p, im.size)
