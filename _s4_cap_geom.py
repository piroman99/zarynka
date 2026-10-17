# -*- coding: utf-8 -*-
"""Точная геометрия новой плашки S4 по коду сборки (2400x1350 -> 1920x1080)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
fnt = ImageFont.truetype(LATO_B, 42)
img = Image.new('RGB', (2400, 1350))
tw = ImageDraw.Draw(img).textlength('а что же обычных людей нет?', font=fnt)
cx, by0 = 1199, 684
pad_x, pad_y = 40, 18
bx0, bx1 = int(cx - tw / 2 - pad_x), int(cx + tw / 2 + pad_x)
by1 = int(by0 + 42 + 2 * pad_y)
print('text width (2400-space):', tw)
print('band 2400:', bx0, by0, bx1, by1)
print('band 1080:', [round(v / 1.25, 1) for v in (bx0, by0, bx1, by1)])

FW, FH = 2400.0, 1350.0
s, ox, oy = 1.5, 0.44, 0.30
for nm, (x, y) in (('band TL', (bx0, by0)), ('band BR', (bx1, by1))):
    vx, vy = x / FW, y / FH
    print('%-8s 1x: %.3f,%.3f  zoom: %.3f,%.3f' % (nm, vx, vy,
                                                  ox + (vx - ox) * s, oy + (vy - oy) * s))
print('видимая область наезда: x 0.147..0.813, y 0.100..0.767')
