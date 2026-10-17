# -*- coding: utf-8 -*-
"""Лист A/B для Ивана: S4 на наезде камеры — было / стало."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

PANELS = [
    ('before', 'БЫЛО', 'подпись уходила вниз и пряталась под подстрочник (#box)', (214, 96, 82)),
    ('zoom', 'СТАЛО', 'подпись м е л ь ч е и сразу под телевизором: на наезде растёт и читается', (126, 214, 128)),
]
W, HEAD = 1400, 96
ims = []
for tag, title, sub, col in PANELS:
    im = Image.open(os.path.join(REV, 'review_113_s4_cap_%s.png' % tag)).convert('RGB')
    im = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
    ims.append((im, title, sub, col))

total_h = sum(im.height + HEAD for im, *_ in ims) + 40
sheet = Image.new('RGB', (W, total_h), (14, 16, 22))
d = ImageDraw.Draw(sheet)
f1 = ImageFont.truetype(GOTHIC, 40)
f2 = ImageFont.truetype(LATO, 24)
y = 0
for im, title, sub, col in ims:
    d.rectangle([0, y, W, y + HEAD - 8], fill=(22, 26, 34))
    d.text((28, y + 8), title, font=f1, fill=col)
    d.text((210, y + 20), sub, font=f2, fill=(226, 220, 206))
    y += HEAD
    sheet.paste(im, (0, y))
    y += im.height
    d.rectangle([0, y - 4, W, y], fill=(60, 66, 80))
out = os.path.join(REV, 'review_113_s4_cap_ab.png')
sheet.save(out)
print(out, sheet.size, os.path.getsize(out), 'B')
