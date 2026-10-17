# -*- coding: utf-8 -*-
"""Лист: S6 без часов (как в сборке) / с табло C1 / с табло C2 + метка S1 без времени."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
import _s6_clock_ab as C

f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 21)
plate = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('RGB').resize((2400, 1350), Image.LANCZOS)

rows = []
rows.append(('S6 · без часов (так сейчас в сборке)', Image.open(os.path.join(HERE, 'assets', 'review', 'review_96_s6_vn_ok.png')).convert('RGB')))
for lb, box in (('S6 · табло C1 на будке', (1898, 322, 2108, 412)),
                ('S6 · табло C2 на правой стойке ворот', (1428, 430, 1600, 512))):
    v = C.clock(plate.copy(), box)
    rows.append((lb, v))
rows.append(('S1 · метка без времени (было «ПОДВОРОТНЯ · 06:07»)',
             Image.open(os.path.join(HERE, 'assets', 'review', 'review_96_s1_vn_ok.png')).convert('RGB')))

W = 1320
pad, lab = 20, 32
imgs = [(lb, im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)) for lb, im in rows]
H = 10 + sum(lab + im.height + pad for _, im in imgs)
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 8
for lb, im in imgs:
    d.text((pad, y), lb, font=f, fill=(232, 200, 140)); y += lab
    sheet.paste(im, (pad, y)); y += im.height + pad
p = os.path.join(HERE, 'assets', 'review', 'review_121_s6_clock.png')
sheet.save(p)
print('sheet ->', os.path.relpath(p, HERE), sheet.size)
