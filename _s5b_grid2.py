# -*- coding: utf-8 -*-
"""Кадр 12 БЕЗ слоя + сетка 100 px: выбрать, куда ставить чип (по фасаду, по центру)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
E = 2400.0
im = Image.open(os.path.join(HERE, '_sat', 's5b_off.png')).convert('RGB')
W, H = im.size
k = W / E
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
for gx in range(0, 2401, 200):
    x = int(gx * k)
    col = (255, 60, 60) if gx == 1200 else (90, 200, 255)
    d.line([(x, 0), (x, H)], fill=col, width=1)
    d.text((x + 2, 2), str(gx), fill=col, font=f)
for gy in range(0, 1351, 100):
    y = int(gy * k)
    col = (255, 60, 60) if gy == 700 else (90, 200, 255)
    d.line([(0, y), (W, y)], fill=col, width=1)
    d.text((2, y + 1), str(gy), fill=col, font=f)
o = os.path.join(HERE, '_sat', 's5b_grid_nolayer.png')
im.resize((1280, 720), Image.LANCZOS).save(o)
print('saved', os.path.relpath(o, HERE))
