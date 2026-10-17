# -*- coding: utf-8 -*-
"""Сетка 25 px по области будки — замерить плоскость стекла/рамы для посадки табло."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
plate = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('RGB')
plate = plate.resize((2400, 1350), Image.LANCZOS)
X0, Y0, X1, Y1 = 1780, 200, 2300, 560
c = plate.crop((X0, Y0, X1, Y1))
S = 3
c = c.resize((c.width * S, c.height * S), Image.LANCZOS)
d = ImageDraw.Draw(c)
f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 16)
for x in range(X0 - X0 % 50, X1, 50):
    px = (x - X0) * S
    d.line([(px, 0), (px, c.height)], fill=(255, 0, 0), width=1)
    d.text((px + 2, 2), str(x), font=f, fill=(255, 255, 0))
for y in range(Y0 - Y0 % 50, Y1, 50):
    py = (y - Y0) * S
    d.line([(0, py), (c.width, py)], fill=(0, 200, 255), width=1)
    d.text((2, py + 1), str(y), font=f, fill=(255, 255, 0))
p = os.path.join(HERE, 'assets', 'review', '_s6_booth_grid.png')
c.save(p)
print(p, c.size)
