# -*- coding: utf-8 -*-
"""Итоговый лист по табло: полный кадр с F1 + кропы F1/F2 в нативном разрешении (x2)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
import _clock_led as L

plate = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('RGB')
plate = plate.resize((2400, 1350), Image.LANCZOS)

F1 = (1852, 306, 2166, 392)
F2 = (1852, 500, 2166, 586)
v1 = L.clock(plate.copy(), F1)
v2 = L.clock(plate.copy(), F2)

f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 21)
W = 1320
pad, lab = 20, 32

def crop(im, box, p=56, s=2):
    c = im.crop((max(0, box[0] - p), max(0, box[1] - p), min(2400, box[2] + p), min(1350, box[3] + p)))
    return c.resize((c.width * s, c.height * s), Image.LANCZOS)

full = v1.resize((W, int(1350 * W / 2400)), Image.LANCZOS)
c1, c2 = crop(v1, F1), crop(v2, F2)

rows = [('S6-B · табло F1 на раме будки (целиком)', full),
        ('F1 крупно — над окном, на раме', c1),
        ('F2 крупно — ниже окна, на парапете', c2)]
imgs = [(lb, im if im.width <= W else im.resize((W, int(im.height * W / im.width)), Image.LANCZOS))
        for lb, im in rows]
H = 8 + sum(lab + im.height + pad for _, im in imgs)
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 8
for lb, im in imgs:
    d.text((pad, y), lb, font=f, fill=(232, 200, 140)); y += lab
    sheet.paste(im, (pad, y)); y += im.height + pad
p = os.path.join(HERE, 'assets', 'review', 'review_125_s6_clock_f1.png')
sheet.save(p)
print('sheet ->', os.path.relpath(p, HERE), sheet.size)
