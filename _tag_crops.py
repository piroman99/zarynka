# -*- coding: utf-8 -*-
"""Нативные кропы метки сцены (×2) для s4, s5, s5a — проверить глазами, обрезан ли текст."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
names = ['s3.png', 's4.png', 's5.png', 's5a.png', 's6.png', 's7.png']
crops = []
for n in names:
    im = Image.open(os.path.join(FIN, n)).convert('RGB')
    k = im.size[0] / 2400.0
    box = (int(50 * k), int(50 * k), int(620 * k), int(150 * k))
    c = im.crop(box)
    crops.append((n, c.resize((c.size[0] * 2, c.size[1] * 2), Image.LANCZOS)))

pad, lab = 12, 24
cw = max(c.size[0] for _, c in crops)
ch = max(c.size[1] for _, c in crops)
sheet = Image.new('RGB', (cw + 2 * pad, len(crops) * (ch + lab + pad) + pad), (14, 16, 22))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
y = pad
for n, c in crops:
    sheet.paste(c, (pad, y))
    d.text((pad, y + ch + 2), n, fill=(214, 218, 226), font=f)
    y += ch + lab + pad
o = os.path.join(HERE, '_sat', 'tags_crop.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
