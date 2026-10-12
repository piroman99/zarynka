# -*- coding: utf-8 -*-
"""Контактный лист текущих кадров пролога S2..S7 (моки) для сверки композиции."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'vn2', 'img', 'prolog')
OUT = os.path.join(HERE, 'assets', 'review', 'review_80_prolog_mocks.png')
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

names = ['s2', 's3', 's4', 's5', 's6', 's7']
CW = 900
pad, gap, hdr = 20, 10, 56
ims = []
for n in names:
    im = Image.open(os.path.join(P, n + '.png')).convert('RGB')
    ims.append((n, im.resize((CW, round(im.height * CW / im.width)), Image.LANCZOS)))
PH = ims[0][1].height
cols, rows = 2, 3
W = pad * 2 + cols * CW + (cols - 1) * gap
H = hdr + rows * (PH + 30 + gap) + pad
c = Image.new('RGB', (W, H), (13, 14, 19))
d = ImageDraw.Draw(c)
d.text((pad, 14), 'Пролог — текущие кадры-моки S2..S7 (vn2/img/prolog)', font=ImageFont.truetype(LATO_B, 26), fill=(226, 186, 104))
for i, (n, im) in enumerate(ims):
    r, k = divmod(i, cols)
    x = pad + k * (CW + gap)
    y = hdr + r * (PH + 30 + gap)
    c.paste(im, (x, y))
    d.rectangle([x, y, x + CW, y + PH], outline=(60, 62, 74))
    d.text((x + 4, y + PH + 4), n.upper(), font=ImageFont.truetype(LATO_B, 22), fill=(240, 236, 228))
c.save(OUT)
print('saved', os.path.relpath(OUT, HERE), c.size)
