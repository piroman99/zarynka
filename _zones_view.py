# -*- coding: utf-8 -*-
"""Показать, ГДЕ именно измеряются зоны (лоб/щетина) на базовом спрайте,
и вырезать эти зоны крупно для базы, OLD и вариантов."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
V2 = os.path.join(GEN, '_sergey_v2')
REV = os.path.join(HERE, 'assets', 'review')

ZONES = {'лоб': (.34, .56, .10, .20), 'щетина': (.34, .66, .30, .38)}
FILES = [('base', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
         ('smile OLD', os.path.join(GEN, 'sergey_smile_0.jpg')),
         ('smile flux v2', os.path.join(V2, 'sergey_smile__flux-2_0.jpg')),
         ('smile gpt v2', os.path.join(V2, 'sergey_smile__gpt-image-2_0.png'))]

# 1) где зоны на базе
im = Image.open(FILES[0][1]).convert('RGB')
d = ImageDraw.Draw(im)
w, h = im.size
for nm, (x0, x1, y0, y1) in ZONES.items():
    d.rectangle([w * x0, h * y0, w * x1, h * y1], outline=(255, 0, 0), width=4)
    d.text((w * x0 + 6, h * y0 + 4), nm, fill=(255, 0, 0))
p0 = os.path.join(REV, 'review_75_zones.png')
im.resize((760, int(h * 760 / w)), Image.LANCZOS).save(p0)
print(p0)

# 2) зоны крупно, одна строка на файл
rows = []
for label, p in FILES:
    src = Image.open(p).convert('RGB')
    w, h = src.size
    parts = []
    for nm, (x0, x1, y0, y1) in ZONES.items():
        z = src.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))
        z = z.resize((640, int(z.height * 640 / z.width)), Image.LANCZOS)
        parts.append((nm, z))
    rows.append((label, parts))

th = max(z.height for _, parts in rows for _, z in parts)
sheet = Image.new('RGB', (1280, (th + 24) * len(rows)), (12, 14, 20))
dd = ImageDraw.Draw(sheet)
for ri, (label, parts) in enumerate(rows):
    y = ri * (th + 24)
    dd.text((6, y + 6), label, fill=(255, 255, 255))
    for ci, (nm, z) in enumerate(parts):
        sheet.paste(z, (ci * 640, y + 24))
        dd.text((ci * 640 + 6, y + 30), nm, fill=(255, 220, 120))
p1 = os.path.join(REV, 'review_76_zones_zoom.png')
sheet.save(p1)
print(p1, sheet.size)
