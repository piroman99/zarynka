# -*- coding: utf-8 -*-
"""Проверка вырезки спрайтов: накладка на цветной фон + границы."""
import os
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(H, 'vn2', 'img', 'char')
REV = os.path.join(H, 'assets', 'review')
tiles = []
for nm in ('kate.png', 'sergey.png'):
    im = Image.open(os.path.join(C, nm)).convert('RGBA')
    bg = Image.new('RGB', im.size, (60, 120, 200))
    bg.paste(im, (0, 0), im)
    tiles.append((nm, bg))
cw, ch = 520, 690
sheet = Image.new('RGB', (len(tiles) * (cw + 10) + 10, ch + 30), (20, 22, 28))
from PIL import ImageDraw
d = ImageDraw.Draw(sheet)
for i, (nm, im) in enumerate(tiles):
    im.thumbnail((cw, ch), Image.LANCZOS)
    x = 10 + i * (cw + 10)
    sheet.paste(im, (x, 24))
    d.text((x, 6), nm + ' (вырезка на синем)', fill=(255, 255, 255))
sheet.save(os.path.join(REV, 'review_73_cutout.png'))
print('->', sheet.size)
