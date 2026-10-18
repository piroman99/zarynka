# -*- coding: utf-8 -*-
"""Что можно поставить вместо кадра «Кейт в платье»: готовые 16:9 кандидаты."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
items = [
    ("kate_reception_vn_0.png (1672x941)", 'assets/gen/kate_reception_vn_0.png'),
    ("kate_reception_0.png (1672x941)", 'assets/gen/kate_reception_0.png'),
    ("kate_overalls_0.png (1087x1447)", 'assets/gen/kate_overalls_0.png'),
    ("sprites/kate_overalls.png (канон-спрайт)", 'assets/sprites/kate_overalls.png'),
]
CW = 900
PAD, LBL = 14, 30
cells = []
for lab, rel in items:
    im = Image.open(os.path.join(HERE, rel))
    if im.mode == 'RGBA':
        bg = Image.new('RGB', im.size, (30, 32, 38))
        bg.paste(im, (0, 0), im)
        im = bg
    im = im.convert('RGB')
    k = CW / im.width
    cells.append((lab, im.resize((CW, max(1, round(im.height * k))), Image.LANCZOS)))
Hh = PAD + 2 * (LBL + max(c[1].height for c in cells[:2]) + PAD)
sheet = Image.new('RGB', (2 * CW + 3 * PAD, Hh), (18, 20, 26))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
x = PAD
for i, (lab, im) in enumerate(cells[:2]):
    d.text((x, PAD), lab, fill=(235, 232, 226), font=f)
    sheet.paste(im, (x, PAD + LBL))
    x += CW + PAD
x = PAD
base = PAD + LBL + max(c[1].height for c in cells[:2]) + PAD
for i, (lab, im) in enumerate(cells[2:]):
    d.text((x, base), lab, fill=(235, 232, 226), font=f)
    sheet.paste(im, (x, base + LBL))
    x += CW + PAD
out = os.path.join(HERE, 'assets', 'review', 'review_104_kate_candidates.png')
sheet.save(out)
print('saved', os.path.relpath(out, HERE), sheet.size)
