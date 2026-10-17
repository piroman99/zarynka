# -*- coding: utf-8 -*-
"""Лист для Ивана: было (наезд, мелкая низкая подпись) / стало в покое / стало на наезде."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
LATO = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

PANELS = [
    ('review_113_s4_cap_before.png', 'БЫЛО', 'кегль 52, подпись внизу — на наезде уходила под подстрочник', (214, 96, 82)),
    ('review_113_s4_cap_wide.png', 'СТАЛО · покой', 'кегль 61 = 94% ширины экрана ТВ, сразу под телевизором', (126, 214, 128)),
    ('review_113_s4_cap_zoom.png', 'СТАЛО · наезд 1.5x', 'растёт до 91%, до подстрочника 101 px — не перекрывается', (126, 214, 128)),
]
W, HEAD = 1400, 78
ims = []
for fn, title, sub, col in PANELS:
    im = Image.open(os.path.join(REV, fn)).convert('RGB')
    im = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
    ims.append((im, title, sub, col))

total_h = sum(im.height + HEAD for im, *_ in ims)
sheet = Image.new('RGB', (W, total_h), (14, 16, 22))
d = ImageDraw.Draw(sheet)
f1 = ImageFont.truetype(GOTHIC, 34)
f2 = ImageFont.truetype(LATO, 22)
y = 0
for im, title, sub, col in ims:
    d.rectangle([0, y, W, y + HEAD - 6], fill=(22, 26, 34))
    d.text((24, y + 8), title, font=f1, fill=col)
    d.text((400, y + 26), sub, font=f2, fill=(226, 220, 206))
    y += HEAD
    sheet.paste(im, (0, y))
    y += im.height
    d.rectangle([0, y - 3, W, y], fill=(60, 66, 80))
out = os.path.join(REV, 'review_114_s4_caption_fit.png')
sheet.save(out)
print(out, sheet.size, os.path.getsize(out), 'B')
