# -*- coding: utf-8 -*-
"""Лист S6-A: сверху сырая плашка flux-2, снизу — как кадр стоит в VN (узел 7)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PLATE = os.path.join(HERE, 'assets', 'gen', 'prologfin7_s6_a_0.jpg')
SHOT = os.path.join(HERE, 'assets', 'review', 'review_96_s6_vn_ok.png')
OUT = os.path.join(HERE, 'assets', 'review', 'review_115_s6_a.png')

W = 1400
FONT = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
f = ImageFont.truetype(FONT, 22)

panels = []
for p, label in ((PLATE, 'ПЛАШКА flux-2 · S6-A (арка КПП, рассвет)'),
                 (SHOT, 'В СБОРКЕ vn2 · узел 7')):
    im = Image.open(p).convert('RGB')
    h = int(im.height * W / im.width)
    panels.append((im.resize((W, h), Image.LANCZOS), label))

pad, top = 24, 46
H = top + sum(p.height + pad for p, _ in panels) + 10
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 12
for im, label in panels:
    d.text((pad, y), label, font=f, fill=(232, 200, 140))
    y += top - 12
    sheet.paste(im, (pad, y))
    y += im.height + pad
sheet.save(OUT)
print('sheet ->', os.path.relpath(OUT, HERE), sheet.size)

# временный снимок больше не нужен
os.remove(SHOT)
