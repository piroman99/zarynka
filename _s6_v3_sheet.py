# -*- coding: utf-8 -*-
"""Лист S6 v3 (пара из БЛ): A и B целиком + кроп пары в нативном разрешении."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'review', 'review_118_s6_couple.png')
f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 20)

items = [('A · пара в середине очереди', 'assets/gen/s6_gpt3_a_0.png', (0.18, 0.30, 0.72, 0.95)),
         ('B · пара на переднем плане', 'assets/gen/s6_gpt3_b_0.png', (0.02, 0.20, 0.56, 0.98))]
W = 1360
rows = []
for label, rel, box in items:
    im = Image.open(os.path.join(HERE, rel)).convert('RGB')
    w, h = im.size
    full = im.resize((W, int(h * W / w)), Image.LANCZOS)
    c = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    cw = W // 2
    c = c.resize((cw, int(c.height * cw / c.width)), Image.LANCZOS)
    rows.append((label, full, c))
    print(rel, im.size, 'crop', c.size)

pad, lab_h = 20, 34
H = 12 + sum(lab_h + full.height + 8 + lab_h + crop.height + pad for _, full, crop in rows)
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 8
for label, full, crop in rows:
    d.text((pad, y), label, font=f, fill=(232, 200, 140)); y += lab_h
    sheet.paste(full, (pad, y)); y += full.height + 8
    d.text((pad, y), 'пара крупно (Женя с книгой, Семён отвёрнут)', font=f, fill=(150, 190, 230))
    y += lab_h
    sheet.paste(crop, (pad, y)); y += crop.height + pad
sheet.save(OUT)
print('sheet ->', os.path.relpath(OUT, HERE), sheet.size)
