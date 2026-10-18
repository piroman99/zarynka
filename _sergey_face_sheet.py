# -*- coding: utf-8 -*-
"""Крупный кроп лица: база vs эмоции. Видно, где поехал возраст/морщины/щетина."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
OUT = os.path.join(HERE, 'assets', 'review', 'review_72_sergey_faces.png')

FILES = [('база (canon)', 'sergey_eng_old__flux-2_0.jpg'),
         ('smile', 'sergey_smile_0.jpg'),
         ('concerned', 'sergey_concerned_0.jpg')]

tiles = []
for label, f in FILES:
    im = Image.open(os.path.join(GEN, f)).convert('RGB')
    w, h = im.size
    # лицо: верхние 42%, по центру
    box = (int(w * .18), int(h * .02), int(w * .82), int(h * .46))
    face = im.crop(box)
    tw = 620
    face = face.resize((tw, int(face.height * tw / face.width)), Image.LANCZOS)
    tiles.append((label, face))

th = max(t[1].height for t in tiles)
sheet = Image.new('RGB', (sum(t[1].width for t in tiles), th + 26), (12, 14, 20))
d = ImageDraw.Draw(sheet)
x = 0
for label, im in tiles:
    sheet.paste(im, (x, 26))
    d.text((x + 8, 8), label, fill=(255, 255, 255))
    x += im.width
sheet.save(OUT)
print(OUT, sheet.size)
