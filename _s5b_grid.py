# -*- coding: utf-8 -*-
"""Кадр 12 с сеткой 200 px (в 2400-пространстве) и осевой линией: видно, где чип
относительно центра кадра и фасада."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
E = 2400.0
im = Image.open(os.path.join(HERE, '_sat', 's5b_on.png')).convert('RGB')
W, H = im.size
k = W / E
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
for gx in range(0, 2401, 200):
    x = int(gx * k)
    col = (255, 60, 60) if gx == 1200 else (90, 200, 255)
    d.line([(x, 0), (x, H)], fill=col, width=1)
    d.text((x + 2, 2), str(gx), fill=col, font=f)
for gy in range(0, 1351, 200):
    y = int(gy * k)
    d.line([(0, y), (W, y)], fill=(90, 200, 255), width=1)
    d.text((2, y + 1), str(gy), fill=(90, 200, 255), font=f)
# рамка чипа (заданная) и его центр
bx = [int(v * k) for v in (560, 830, 1360, 920)]
d.rectangle(bx, outline=(120, 255, 120), width=2)
d.line([(int(960 * k), int(800 * k)), (int(960 * k), int(950 * k))],
       fill=(120, 255, 120), width=1)
o = os.path.join(HERE, '_sat', 's5b_grid.png')
im.resize((1280, 720), Image.LANCZOS).save(o)
print('saved', os.path.relpath(o, HERE))
