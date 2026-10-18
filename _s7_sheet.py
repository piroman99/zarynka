# -*- coding: utf-8 -*-
"""Лист S7: сверху S6 (что уже есть в сборке), ниже два варианта S7 — видно, повтор или нет."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 21)

items = [
    ('S6 (уже в сборке) · средний план у ворот, пара Женя+Семён',
     'assets/final/prolog/s6.png'),
    ('S7 · вариант A — верхний ракурс, очередь-река по аллее',
     'assets/gen/s7_gpt_a_0.png'),
    ('S7 · вариант B — от ворот вниз по аллее, людская река в глубину',
     'assets/gen/s7_gpt_b_0.png'),
]

W = 1320
pad, lab = 20, 32
imgs = []
for label, rel in items:
    im = Image.open(os.path.join(HERE, rel)).convert('RGB')
    im = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
    imgs.append((label, im))
    print(rel, im.size)

H = 10 + sum(lab + im.height + pad for _, im in imgs)
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 8
for label, im in imgs:
    d.text((pad, y), label, font=f, fill=(232, 200, 140)); y += lab
    sheet.paste(im, (pad, y)); y += im.height + pad
p = os.path.join(HERE, 'assets', 'review', 'review_127_s7_ab.png')
sheet.save(p)
print('sheet ->', os.path.relpath(p, HERE), sheet.size)
