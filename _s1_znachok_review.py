# -*- coding: utf-8 -*-
"""Лист проверки пасхалки S1: «потерянный значок в луже».
Собирает: (верх) кадр S1 с отметкой зоны, (низ) увеличение лужи.
Выход: assets/review/review_78_s1_znachok.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', 'mock', 'prolog', 's1_base.png')
OUT = os.path.join(HERE, 'assets', 'review', 'review_78_s1_znachok.png')
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'

W = 2020
GAP = 24
im = Image.open(SRC).convert('RGB')
sx = W / im.width
full = im.resize((W, int(im.height * sx)), Image.LANCZOS)

# зона лужи (координаты кадра 2400x1350)
BOX = (660, 1120, 1660, 1350)
box = im.crop(BOX)
zoom = box.resize((W, int(box.height * W / box.width)), Image.LANCZOS)

H = full.height + GAP + zoom.height + GAP
sheet = Image.new('RGB', (W, H), (14, 16, 22))
sheet.paste(full, (0, 0))
sheet.paste(zoom, (0, full.height + GAP))

d = ImageDraw.Draw(sheet)
fb = ImageFont.truetype(LATO_B, 34)
# отметка зоны на полном кадре
rb = [int(BOX[0] * sx), int(BOX[1] * sx), int(BOX[2] * sx), int(BOX[3] * sx)]
d.rectangle(rb, outline=(220, 80, 70), width=6)
# подпись врезки
d.rectangle([0, full.height + GAP, W, full.height + GAP + 46], fill=(20, 22, 30))
d.text((16, full.height + GAP + 6),
       'S1 подворотня — увеличение лужи: значок-пятиугольник (пасхалка)',
       font=fb, fill=(232, 200, 150))
sheet.save(OUT)
print('->', os.path.relpath(OUT, HERE), sheet.size)
