# -*- coding: utf-8 -*-
"""Контактный лист кандидатов на субботний скриншот."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '_sat')
names = ['rec03', 'rec16', 'rec34', 'rec50', 'star01', 's6', 's7']
cw, ch, cols = 640, 360, 3
rows = (len(names) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * ch), (12, 14, 20))
d = ImageDraw.Draw(sheet)
for i, nm in enumerate(names):
    p = os.path.join(OUT, 'sat_%s.png' % nm)
    im = Image.open(p).convert('RGB').resize((cw, ch), Image.LANCZOS)
    x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(45, 50, 62))
    d.text((x + 8, y + 6), nm, fill=(255, 255, 255))
sheet.save(os.path.join(OUT, 'sat_sheet.png'))
print('SHEET', sheet.size)
for nm in names:
    p = os.path.join(OUT, 'sat_%s.png' % nm)
    print(nm, os.path.getsize(p) // 1024, 'KB')
