# -*- coding: utf-8 -*-
"""Подбор полосы лозунга на стенд кадра 11-A: ширины строк и мок в 2400x1350."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
OUT = os.path.join(HERE, '_sat')
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
CREAM = (246, 238, 222)
WARM = (252, 226, 170)
RED = (168, 40, 34)

im0 = Image.open(os.path.join(GEN, 's5a_a__gpt-image-2_0.png')).convert('RGB')
FW, FH = 2400, 1350
base = im0.resize((FW, FH), Image.LANCZOS)
d = ImageDraw.Draw(base)


def tw(t, s):
    return d.textlength(t, font=ImageFont.truetype(GOTHIC, s))


L1, L2 = 'МАРС — ДЕЛО ОБЩЕЕ!', 'ДАЁШЬ МАРС ДЛЯ ВСЕХ!'
for s in (76, 68, 62, 56, 52):
    print('L1 %d -> %.0f   L2 %d -> %.0f' % (s, tw(L1, s), s, tw(L2, s)))

# стенд (по сетке 5%): x 60..96 %, y 22..72 %
BX0, BX1, BY0, BY1 = 1440, 2304, 297, 972
print('стенд', (BX0, BY0, BX1, BY1), 'ширина', BX1 - BX0, 'высота', BY1 - BY0)

# полоса = плакат внутри стенда с полями 4% ширины кадра
band = (BX0 + 60, BY0 + 70, BX1 - 60, BY1 - 70)
bw = band[2] - band[0]
print('полоса', band, 'ширина', bw)
size1 = 76
while tw(L1, size1) > bw * 0.90 and size1 > 30:
    size1 -= 1
size2 = 62
while tw(L2, size2) > bw * 0.90 and size2 > 30:
    size2 -= 1
print('подобрано: L1 %d (%.0f), L2 %d (%.0f), лимит %.0f' % (size1, tw(L1, size1), size2, tw(L2, size2), bw * 0.90))

ov = Image.new('RGBA', base.size, (0, 0, 0, 0))
ImageDraw.Draw(ov).rounded_rectangle(band, radius=20, fill=RED + (232,))
ov = ov.filter(ImageFilter.GaussianBlur(10))
base = Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')
d = ImageDraw.Draw(base)
cx = (band[0] + band[2]) / 2
h1 = size1
gap = 22
total = h1 + gap + size2
y0 = (band[1] + band[3]) / 2 - total / 2
d.text((cx, y0), L1, font=ImageFont.truetype(GOTHIC, size1), fill=CREAM, anchor='ma')
d.text((cx, y0 + h1 + gap), L2, font=ImageFont.truetype(GOTHIC, size2), fill=WARM, anchor='ma')
p = os.path.join(OUT, 's5a_band_mock.png')
base.resize((1672, 941), Image.LANCZOS).save(p)
print('saved', p)
