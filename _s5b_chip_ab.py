# -*- coding: utf-8 -*-
"""Кроп чипа кадра 12 в живом демо: со слоем и без, один и тот же участок, ×3."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
E = 2400.0
pairs = []
for name, lab in (('s5b_on.png', 'со слоем'), ('s5b_off.png', 'без слоя')):
    im = Image.open(os.path.join(HERE, '_sat', name)).convert('RGB')
    W, H = im.size
    k = W / E
    box = (int(480 * k), int(790 * k), int(1460 * k), int(960 * k))
    c = im.crop(box)
    c = c.resize((c.size[0] * 3, c.size[1] * 3), Image.LANCZOS)
    pairs.append((lab, c))
    print(lab, 'crop', box, '->', c.size)

pad, lab_h = 12, 24
cw = max(c.size[0] for _, c in pairs)
ch = max(c.size[1] for _, c in pairs)
sheet = Image.new('RGB', (cw + 2 * pad, len(pairs) * (ch + lab_h + pad) + pad), (14, 16, 22))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
y = pad
for t, c in pairs:
    sheet.paste(c, (pad, y))
    d.text((pad, y + ch + 2), t, fill=(214, 218, 226), font=f)
    y += ch + lab_h + pad
o = os.path.join(HERE, '_sat', 's5b_chip_ab.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
