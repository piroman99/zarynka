# -*- coding: utf-8 -*-
"""Максимальный зум: только лоб (морщины) и только усы/подбородок (щетина)."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
V2 = os.path.join(GEN, '_sergey_v2')
REV = os.path.join(HERE, 'assets', 'review')

FILES = [('base', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
         ('OLD', os.path.join(GEN, 'sergey_smile_0.jpg')),
         ('flux v2', os.path.join(V2, 'sergey_smile__flux-2_0.jpg')),
         ('gpt v2', os.path.join(V2, 'sergey_smile__gpt-image-2_0.png'))]

REG = {'лоб': (.36, .62, .115, .215), 'усы/подбородок': (.38, .64, .285, .355)}
TW = 640

rows = []
for label, p in FILES:
    src = Image.open(p).convert('RGB')
    w, h = src.size
    parts = []
    for nm, (x0, x1, y0, y1) in REG.items():
        z = src.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
        z = z.resize((TW, int(z.height * TW / z.width)), Image.LANCZOS)
        parts.append((nm, z))
    rows.append((label, parts))

th = max(z.height for _, parts in rows for _, z in parts)
sheet = Image.new('RGB', (TW * 2, (th + 26) * len(rows)), (12, 14, 20))
d = ImageDraw.Draw(sheet)
for ri, (label, parts) in enumerate(rows):
    y = ri * (th + 26)
    d.text((6, y + 8), label, fill=(255, 255, 255))
    for ci, (nm, z) in enumerate(parts):
        sheet.paste(z, (ci * TW, y + 26))
        d.text((ci * TW + 6, y + 30), nm, fill=(255, 220, 120))
p = os.path.join(REV, 'review_77_sergey_zoom_tight.png')
sheet.save(p)
print(p, sheet.size)
