# -*- coding: utf-8 -*-
"""Лист лиц: база + варианты эмоций (flux-2 / gpt-image-2), крупно."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
V2 = os.path.join(GEN, '_sergey_v2')
OUT = os.path.join(HERE, 'assets', 'review', 'review_73_sergey_emo_v2.png')

rows = [
    [('база (canon)', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
     ('smile OLD (в сборке)', os.path.join(GEN, 'sergey_smile_0.jpg')),
     ('smile flux-2 v2', os.path.join(V2, 'sergey_smile__flux-2_0.jpg')),
     ('smile gpt-image-2 v2', os.path.join(V2, 'sergey_smile__gpt-image-2_0.png'))],
    [('база (canon)', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
     ('concerned OLD (в сборке)', os.path.join(GEN, 'sergey_concerned_0.jpg')),
     ('concerned flux-2 v2', os.path.join(V2, 'sergey_concerned__flux-2_0.jpg')),
     ('concerned gpt-image-2 v2', os.path.join(V2, 'sergey_concerned__gpt-image-2_0.png'))],
]

tw = 470
tiles = []
for row in rows:
    r = []
    for label, p in row:
        im = Image.open(p).convert('RGB')
        w, h = im.size
        box = (int(w * .20), int(h * .03), int(w * .80), int(h * .45))
        face = im.crop(box)
        face = face.resize((tw, int(face.height * tw / face.width)), Image.LANCZOS)
        r.append((label, face))
    tiles.append(r)

th = max(t[1].height for row in tiles for t in row)
sheet = Image.new('RGB', (tw * 4, (th + 26) * len(tiles)), (12, 14, 20))
d = ImageDraw.Draw(sheet)
for ri, row in enumerate(tiles):
    for ci, (label, im) in enumerate(row):
        x, y = ci * tw, ri * (th + 26)
        sheet.paste(im, (x, y + 26))
        d.text((x + 8, y + 8), label, fill=(255, 255, 255))
sheet.save(OUT)
print(OUT, sheet.size)
