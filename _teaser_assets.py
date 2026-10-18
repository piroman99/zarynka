# -*- coding: utf-8 -*-
"""Лист ассетов тизера: логотипы + кадры с Екатериной."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
items = [
    ("logo_a_0 (в тизере)", 'assets/gen/logo_a_0.jpg'),
    ("logo_b_0", 'assets/gen/logo_b_0.jpg'),
    ("logo_c_0", 'assets/gen/logo_c_0.jpg'),
    ("vn2/img/logo.png (титул VN)", 'vn2/img/logo.png'),
    ("ok_reception_fix2_0 (t=14-16)", 'assets/gen/ok_reception_fix2_0.jpg'),
    ("ok_x_kate_moon_0 (t=24)", 'assets/gen/ok_x_kate_moon_0.jpg'),
]
CW = 620
PAD, LBL = 14, 30
cells = []
for lab, rel in items:
    p = os.path.join(HERE, rel)
    im = Image.open(p).convert('RGB')
    k = CW / im.width
    cells.append((lab, im.resize((CW, max(1, round(im.height * k))), Image.LANCZOS)))

rows = [(cells[0:3], 'logos'), (cells[3:], 'frames')]
H = PAD
for row, _ in rows:
    H += LBL + max(c[1].height for c in row) + PAD
sheet = Image.new('RGB', (3 * CW + 4 * PAD, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
y = PAD
for row, _ in rows:
    for i, (lab, im) in enumerate(row):
        x = PAD + i * (CW + PAD)
        d.text((x, y), lab, fill=(235, 232, 226), font=f)
        sheet.paste(im, (x, y + LBL))
    y += LBL + max(c[1].height for c in row) + PAD
out = os.path.join(HERE, 'assets', 'review', 'review_103_teaser_assets.png')
sheet.save(out)
print('saved', os.path.relpath(out, HERE), sheet.size)
