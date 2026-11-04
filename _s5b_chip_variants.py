# -*- coding: utf-8 -*-
"""Макет: куда ставить чип «ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ» на кадре 12 (s5b).
A — по центру, на фасаде над входом; B — по центру, ниже (на ступенях);
C — без чипа (субтитр и так это говорит). Лист на глаз."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GOTHIC = '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf'
GOLD = (255, 210, 120)
E = 2400.0
TXT = 'ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ'

base = Image.open(os.path.join(HERE, '_sat', 's5b_off.png')).convert('RGB')
W, H = base.size
k = W / E
d0 = ImageDraw.Draw(base)
tw = d0.textlength(TXT, font=ImageFont.truetype(GOTHIC, 46))
print('ширина текста 46 = %.0f (в 2400)' % tw)


def chip(img, cy, size=46, alpha=150, pad=49):
    w = int(tw + 2 * pad)
    x0, x1 = int(1200 - w / 2), int(1200 + w / 2)
    y0, y1 = int(cy - 45), int(cy + 45)
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=6,
                                         fill=(6, 8, 14, alpha))
    img = Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB')
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(GOTHIC, max(8, int(size * k)))
    d.text((1200 * k, cy * k), TXT, font=f, fill=GOLD, anchor='mm')
    return img


vA = chip(base, 735)     # на фасаде над входом
vB = chip(base, 875)     # ниже, на ступенях
vC = base.copy()         # без чипа

items = [('A — по центру, на фасаде над входом', vA),
         ('B — по центру, ниже (на ступенях)', vB),
         ('C — без чипа (субтитр это уже говорит)', vC)]
cw = 1100
ch = int(cw * 720 / 1280)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
pad, lab = 12, 26
sheet = Image.new('RGB', (cw + 2 * pad, len(items) * (ch + lab + pad) + pad), (14, 16, 22))
d = ImageDraw.Draw(sheet)
y = pad
for t, im in items:
    sheet.paste(im.resize((cw, ch), Image.LANCZOS), (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 4), t, fill=(214, 218, 226), font=f)
    y += ch + lab + pad
o = os.path.join(HERE, '_sat', 's5b_chip_variants.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
