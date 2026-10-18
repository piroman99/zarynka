# -*- coding: utf-8 -*-
"""Кроп лица Кати (база vs новая smile) в отдельный небольшой PNG для просмотра."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
K2 = os.path.join(GEN, '_kate_v2')
OUT = os.path.join(HERE, 'assets', 'review', 'review_80_kate_face.png')

FILES = [('base', os.path.join(GEN, 'kate_overalls_0.png')),
         ('smile', os.path.join(K2, 'kate_smile__gpt-image-2_0.png'))]
TW = 520
tiles = []
for label, p in FILES:
    im = Image.open(p).convert('RGB')
    w, h = im.size
    f = im.crop((int(w * .26), int(h * .06), int(w * .74), int(h * .34)))
    f = f.resize((TW, int(f.height * TW / f.width)), Image.LANCZOS)
    tiles.append((label, f))
th = tiles[0][1].height
sheet = Image.new('RGB', (TW * 2, th + 22), (15, 15, 18))
d = ImageDraw.Draw(sheet)
for i, (label, im) in enumerate(tiles):
    sheet.paste(im, (i * TW, 22))
    d.text((i * TW + 6, 6), label, fill=(255, 255, 255))
sheet.save(OUT, optimize=True)
print(OUT, sheet.size, os.path.getsize(OUT))
