# -*- coding: utf-8 -*-
"""Лист-проверка gpt-image-2 S6: полный кадр + кроп вывески (читаемость кириллицы)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'review', 'review_116_s6_gpt.png')
F = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
f = ImageFont.truetype(F, 20)

items = [('A · широкий план', 'assets/gen/s6_gpt_a_0.png'),
         ('B · средний план', 'assets/gen/s6_gpt_b_0.png')]
W = 1360
rows = []
for label, rel in items:
    im = Image.open(os.path.join(HERE, rel)).convert('RGB')
    print(rel, im.size)
    h = int(im.height * W / im.width)
    full = im.resize((W, h), Image.LANCZOS)
    # верхняя треть (арка с вывеской) крупно
    top = im.crop((0, 0, im.width, int(im.height * 0.42)))
    th = int(top.height * (W / 2) / top.width)
    top = top.resize((W // 2, th), Image.LANCZOS)
    rows.append((label, full, top))

pad, top_h = 20, 40
H = top_h + sum(full.height + pad + top_h + top.height + pad for _, full, top in rows)
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 10
for label, full, top in rows:
    d.text((pad, y), label, font=f, fill=(232, 200, 140))
    y += top_h - 10
    sheet.paste(full, (pad, y))
    y += full.height + pad - 10
    d.text((pad, y), 'вывеска крупно', font=f, fill=(150, 190, 230))
    y += top_h - 10
    sheet.paste(top, (pad, y))
    y += top.height + pad
sheet.save(OUT)
print('sheet ->', os.path.relpath(OUT, HERE), sheet.size)
