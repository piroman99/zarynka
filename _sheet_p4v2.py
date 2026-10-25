# -*- coding: utf-8 -*-
"""Лист для Ивана: P4 v2 — вариант A против B + как это стоит в игре (стр. 35)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
OUT = os.path.join(HERE, '_sat', 'sheet_p4v2.png')

W = 1500
PAD = 24
LBL = 40
F = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 30)

items = [
    ('P4 v2 · вариант A — общий план, оба лица', os.path.join(GEN, 'cg_p4v2_a__gpt-image-2_0.png')),
    ('P4 v2 · вариант B — через плечо Екатерины', os.path.join(GEN, 'cg_p4v2_b__gpt-image-2_0.png')),
    ('в игре: стр. 35 «Сергей потер переносицу…»', os.path.join(HERE, '_sat', 'cg_cg35_1.png')),
    ('в игре: стр. 37 «При всех наших возможностях…»', os.path.join(HERE, '_sat', 'cg_cg35_2.png')),
    ('до выхода Екатерины (стр. 21 — только Сергей)', os.path.join(HERE, '_sat', 'cg_kate_no.png')),
    ('выход Екатерины (стр. 23 — «Добрый день»)', os.path.join(HERE, '_sat', 'cg_kate_yes.png')),
    ('грустный CG держится до стр. 61', os.path.join(HERE, '_sat', 'cg_cg50.png')),
]

rows = []
for title, path in items:
    im = Image.open(path).convert('RGB')
    im = im.resize((W - 2 * PAD, int(im.height * (W - 2 * PAD) / im.width)), Image.LANCZOS)
    rows.append((title, im))

H = sum(LBL + im.height + PAD for _, im in rows) + PAD
sheet = Image.new('RGB', (W, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = PAD
for title, im in rows:
    d.text((PAD, y + 4), title, font=F, fill=(240, 226, 190))
    y += LBL
    sheet.paste(im, (PAD, y))
    y += im.height + PAD
sheet.save(OUT)
print(OUT, sheet.size)
