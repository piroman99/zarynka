# -*- coding: utf-8 -*-
"""Показать содержимое оверлеев моков пролога (на сером фоне), чтобы понять их геометрию."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(HERE, 'assets', 'mock', 'prolog')
OUT = os.path.join(HERE, 'assets', 'review', 'review_81_ovl.png')
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
names = ['s1_poster', 's3_q1', 's3_q2', 's3_q3', 's4_video', 's4_q',
         's5_posters', 's5_soviet', 's5_seats']
CW = 760
ims = []
for n in names:
    ov = Image.open(os.path.join(M, n + '.png')).convert('RGBA')
    bg = Image.new('RGBA', ov.size, (70, 72, 84, 255))
    im = Image.alpha_composite(bg, ov).convert('RGB')
    ims.append((n, im.resize((CW, round(im.height * CW / im.width)), Image.LANCZOS)))
PH = ims[0][1].height
cols = 3; rows = (len(ims) + cols - 1) // cols
pad, gap, caph, hdr = 16, 8, 30, 48
W = pad * 2 + cols * CW + (cols - 1) * gap
H = hdr + rows * (PH + caph + gap) + pad
c = Image.new('RGB', (W, H), (13, 14, 19)); d = ImageDraw.Draw(c)
d.text((pad, 12), 'Оверлеи моков пролога (на сером)', font=ImageFont.truetype(LATO_B, 24), fill=(226, 186, 104))
for i, (n, im) in enumerate(ims):
    r, k = divmod(i, cols); x = pad + k * (CW + gap); y = hdr + r * (PH + caph + gap)
    c.paste(im, (x, y)); d.rectangle([x, y, x + CW, y + PH], outline=(60, 62, 74))
    d.text((x + 4, y + PH + 4), n, font=ImageFont.truetype(LATO_B, 20), fill=(240, 236, 228))
c.save(OUT); print('saved', os.path.relpath(OUT, HERE), c.size)
