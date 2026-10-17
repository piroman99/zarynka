# -*- coding: utf-8 -*-
"""Лист S6 v2: A и B + верх кадра крупно (вывеска)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'review', 'review_117_s6_spring.png')
f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 20)

items = [('A · широкий план — ворота, аллея, очередь в глубину', 'assets/gen/s6_gpt2_a_0.png'),
         ('B · средний план — очередь крупно', 'assets/gen/s6_gpt2_b_0.png')]
W = 1360
rows = []
for label, rel in items:
    im = Image.open(os.path.join(HERE, rel)).convert('RGB')
    print(rel, im.size)
    full = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
    top = im.crop((0, 0, im.width, int(im.height * 0.30)))
    top = top.resize((W // 2, int(top.height * (W // 2) / top.width)), Image.LANCZOS)
    rows.append((label, full, top))

pad, lab_h = 20, 34
H = 12 + sum(lab_h + full.height + 8 + lab_h + top.height + pad for _, full, top in rows)
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 8
for label, full, top in rows:
    d.text((pad, y), label, font=f, fill=(232, 200, 140)); y += lab_h
    sheet.paste(full, (pad, y)); y += full.height + 8
    d.text((pad, y), 'вывеска крупно', font=f, fill=(150, 190, 230)); y += lab_h
    sheet.paste(top, (pad, y)); y += top.height + pad
sheet.save(OUT)
print('sheet ->', os.path.relpath(OUT, HERE), sheet.size)
