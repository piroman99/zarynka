# -*- coding: utf-8 -*-
"""A/B для S1: как есть vs + котобус мелом (пасхалка из мока) на финальной плашке.
Строит assets/review/review_83_s1_katobus.png. Кадры vn2 не перезаписывает."""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'vn2', 'img', 'prolog', 's1.png')
OUT = os.path.join(HERE, 'assets', 'review', 'review_83_s1_katobus.png')
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
random.seed(11)


def chalk(base, box=(150, 620, 470, 800), a=150):
    """Детский рисунок мелом: многолапый кот-автобус (Catbus)."""
    x0, y0, x1, y1 = box
    lay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    C = (236, 232, 216, a)
    w = 4
    d.rounded_rectangle([x0, y0, x1, y1], radius=int((y1 - y0) * 0.35), outline=C, width=w)
    d.polygon([(x0 + 34, y0 + 4), (x0 + 62, y0 - 34), (x0 + 90, y0 + 4)], outline=C, width=w)
    d.polygon([(x1 - 90, y0 + 4), (x1 - 62, y0 - 34), (x1 - 34, y0 + 4)], outline=C, width=w)
    for wx in range(x0 + 30, x1 - 26, 44):
        d.rectangle([wx, y0 + 22, wx + 26, y0 + 52], outline=C, width=w)
    for lx in range(x0 + 22, x1 - 18, 38):
        d.line([(lx, y1), (lx, y1 + 34)], fill=C, width=w)
    d.line([(x1 - 2, y0 + 60), (x1 + 40, y0 + 44), (x1 + 46, y0 + 80)], fill=C, width=w)
    d.ellipse([x1 - 62, y0 + 26, x1 - 48, y0 + 40], outline=C, width=3)
    for k in range(3):
        d.line([(x1 - 60, y0 + 46 + k * 8), (x1 - 6, y0 + 38 + k * 10)], fill=C, width=2)
    lay = lay.filter(ImageFilter.GaussianBlur(0.7))
    return Image.alpha_composite(base.convert('RGBA'), lay).convert('RGB')


src = Image.open(P).convert('RGB')
A = src
B = chalk(src)
CW = 1180
pad, caph, hdr, gap = 20, 44, 78, 12
ims = [(A.resize((CW, round(A.height * CW / A.width)), Image.LANCZOS), 'A · как есть (без пасхалки)'),
       (B.resize((CW, round(B.height * CW / B.width)), Image.LANCZOS), 'B · + котобус мелом на стене (пасхалка S1)')]
PH = ims[0][0].height
H = hdr + sum(im.height + caph + gap for im, _ in ims) + pad
c = Image.new('RGB', (CW + 2 * pad, H), (13, 14, 19)); d = ImageDraw.Draw(c)
d.text((pad, 14), '«ЗАРЯНКА» · S1 — нужна ли пасхалка (котобус) на финальной плашке?',
       font=ImageFont.truetype(LATO_B, 26), fill=(226, 186, 104))
y = hdr
for im, cap in ims:
    c.paste(im, (pad, y)); d.rectangle([pad, y, pad + im.width, y + im.height], outline=(60, 62, 74))
    d.text((pad + 4, y + im.height + 6), cap, font=ImageFont.truetype(LATO_B, 22), fill=(240, 236, 228))
    y += im.height + caph + gap
c.save(OUT); print('saved', os.path.relpath(OUT, HERE), c.size)
