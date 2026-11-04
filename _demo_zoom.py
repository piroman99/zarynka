# -*- coding: utf-8 -*-
"""Крупный просмотр живого демо: верх (метка) и низ (подстрочник) отдельно."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, '_sat', 'demo_s5a.png')).convert('RGB')
W, H = im.size
parts = [('верх · метка', (0, 0, 700, 180)),
         ('низ · подстрочник', (0, int(H * 0.72), W, H))]
crops = []
for t, box in parts:
    c = im.crop(box)
    c = c.resize((c.size[0] * 2, c.size[1] * 2), Image.LANCZOS)
    crops.append((t, c))

pad, lab = 12, 24
cw = max(c.size[0] for _, c in crops)
ch = max(c.size[1] for _, c in crops)
sheet = Image.new('RGB', (cw + 2 * pad, len(crops) * (ch + lab + pad) + pad), (14, 16, 22))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
y = pad
for t, c in crops:
    sheet.paste(c, (pad, y))
    d.text((pad, y + ch + 2), t, fill=(214, 218, 226), font=f)
    y += ch + lab + pad
o = os.path.join(HERE, '_sat', 'demo_zoom.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
