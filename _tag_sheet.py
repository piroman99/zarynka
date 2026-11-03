# -*- coding: utf-8 -*-
"""Лист кропов метки сцены (левый верх) по всем финальным кадрам пролога:
видно, влезает ли текст в чёрную плашку после правки tag()."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
files = sorted(f for f in os.listdir(FIN) if f.endswith('.png'))
crops = []
for f in files:
    im = Image.open(os.path.join(FIN, f)).convert('RGB')
    W, H = im.size
    k = W / 2400.0
    box = (int(40 * k), int(40 * k), int(700 * k), int(170 * k))
    crops.append((f, im.crop(box)))

cw = 640
ch = int(cw * crops[0][1].size[1] / crops[0][1].size[0])
cols = 2
rows = (len(crops) + cols - 1) // cols
pad, lab = 10, 22
sheet = Image.new('RGB', (cols * (cw + pad) + pad, rows * (ch + lab + pad) + pad), (14, 16, 22))
d = ImageDraw.Draw(sheet)
fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
for i, (name, im) in enumerate(crops):
    x = pad + (i % cols) * (cw + pad)
    y = pad + (i // cols) * (ch + lab + pad)
    sheet.paste(im.resize((cw, ch), Image.LANCZOS), (x, y))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((x, y + ch + 3), name, fill=(214, 218, 226), font=fnt)
o = os.path.join(HERE, '_sat', 'tags_all.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size, 'кадров:', len(crops))
