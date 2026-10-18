# -*- coding: utf-8 -*-
"""Лист для заказчика: Старик в игре (стр.0 Сергей / стр.1 Старик) + кромка 4x."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
FB = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
f = lambda s: ImageFont.truetype(FB, s)

p0 = Image.open(os.path.join(REV, 'review_132_reception_p0.png')).convert('RGB')
p1 = Image.open(os.path.join(REV, 'review_132_reception_p1.png')).convert('RGB')
spr = Image.open(os.path.join(HERE, 'assets', 'sprites', 'starik_stern.png')).convert('RGBA')

TW = 700                                   # ширина тайла
TH = int(TW * p0.height / p0.width)
t0 = p0.resize((TW, TH), Image.LANCZOS)
t1 = p1.resize((TW, TH), Image.LANCZOS)

# кромка 4x на тёмном фоне: плечо/пиджак (низ справа)
w, h = spr.size
box = (int(w * 0.30), int(h * 0.70), int(w * 0.62), int(h * 0.92))
crop = spr.crop(box)
z = 4
cz = crop.resize((crop.width * z, crop.height * z), Image.NEAREST)
dark = Image.new('RGB', cz.size, (18, 22, 34))
dark.paste(cz, (0, 0), cz)
tz = dark.resize((TW, TH), Image.LANCZOS)

GAP, HDR = 12, 40
W = TW * 3 + GAP * 2
H = HDR + TH + 34
sheet = Image.new('RGB', (W, H), (14, 16, 22))
d = ImageDraw.Draw(sheet)
d.text((14, 10), 'Старик — спрайт в игре (вырез из starik_0.jpg, деспилл кромки)', font=f(24), fill=(232, 200, 150))
for i, (tile, cap) in enumerate(((t0, 'стр.0 — Сергей'), (t1, 'стр.1 — Старик («клоунада»)'),
                                 (tz, 'кромка пиджака 4x на тёмном'))):
    x = i * (TW + GAP)
    sheet.paste(tile, (x, HDR))
    d.rectangle([x, HDR, x + TW, HDR + TH], outline=(56, 60, 74), width=2)
    d.text((x + 8, HDR + TH + 8), cap, font=f(19), fill=(212, 206, 192))
p = os.path.join(REV, 'review_133_starik_in_game.png')
sheet.save(p)
print('->', os.path.relpath(p, HERE), sheet.size, os.path.getsize(p), 'B')
