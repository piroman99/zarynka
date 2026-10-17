# -*- coding: utf-8 -*-
"""C1 крупно: табло на будке вахтёра. Полный кадр + кроп будки в нативном разрешении."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
import _s6_clock_ab as C

BOX = (1898, 322, 2108, 412)          # табло на будке
plate = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('RGB')
plate = plate.resize((2400, 1350), Image.LANCZOS)
full = C.clock(plate.copy(), BOX)

# кроп будки: нативно, потом 2x
crop_box = (1560, 180, 2320, 700)
crop = full.crop(crop_box)
crop2 = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)

# полный кадр в 1320 px
W = 1320
full_s = full.resize((W, int(full.height * W / full.width)), Image.LANCZOS)

f = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Bold.ttf', 21)
pad, lab = 20, 32
H = 10 + lab + full_s.height + pad + lab + crop2.height + pad
sheet = Image.new('RGB', (W + 2 * pad, H), (18, 20, 26))
d = ImageDraw.Draw(sheet)
y = 8
d.text((pad, y), 'S6-B · табло C1 на будке вахтёра (целиком)', font=f, fill=(232, 200, 140))
y += lab
sheet.paste(full_s, (pad, y)); y += full_s.height + pad
d.text((pad, y), 'кроп будки, нативно x2 — так это видно вблизи', font=f, fill=(150, 190, 230))
y += lab
sheet.paste(crop2, (pad, y)); y += crop2.height + pad
p = os.path.join(HERE, 'assets', 'review', 'review_122_s6_clock_c1.png')
sheet.save(p)
print('sheet ->', os.path.relpath(p, HERE), sheet.size)
print('табло в кадре: %dx%d px (2400-пространство)' % (BOX[2] - BOX[0], BOX[3] - BOX[1]))
