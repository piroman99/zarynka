# -*- coding: utf-8 -*-
"""S1: B (плоский мел) в разных местах/размерах — лист для САМОПРОВЕРКИ, выбрать чистое место.
Не пишет в vn2."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'vn2', 'img', 'prolog', 's1.png')
OUT = os.path.join(HERE, 'assets', 'review', 'review_85_s1_place.png')
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
CHALK = (238, 234, 220)


def draw_katobus(w, h, wd=3):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    C = CHALK + (235,)
    x0, y0, x1, y1 = 4, 34, w - 46, h - 34
    d.rounded_rectangle([x0, y0, x1, y1], radius=int((y1 - y0) * 0.35), outline=C, width=wd)
    d.polygon([(x0 + 22, y0 + 4), (x0 + 40, y0 - 22), (x0 + 58, y0 + 4)], outline=C, width=wd)
    d.polygon([(x1 - 58, y0 + 4), (x1 - 40, y0 - 22), (x1 - 22, y0 + 4)], outline=C, width=wd)
    for wx in range(x0 + 16, x1 - 20, 30):
        d.rectangle([wx, y0 + 14, wx + 18, y0 + 36], outline=C, width=wd)
    for lx in range(x0 + 14, x1 - 12, 26):
        d.line([(lx, y1), (lx, y1 + 20)], fill=C, width=wd)
    d.line([(x1 - 2, y0 + 40), (x1 + 26, y0 + 30), (x1 + 34, y0 + 58)], fill=C, width=wd)
    return im


def put(base, box, wd=3):
    x0, y0, x1, y1 = box
    ch = draw_katobus(x1 - x0, y1 - y0, wd=wd).filter(ImageFilter.GaussianBlur(0.55))
    out = base.convert('RGBA'); out.paste(ch, (x0, y0), ch)
    return out.convert('RGB')


src = Image.open(P).convert('RGB')
places = [
    ('B1 · 320×180 у арки (как было)', (150, 620, 470, 800), 3),
    ('B2 · 250×140 на кирпиче слева от фигуры', (600, 430, 850, 570), 3),
    ('B3 · 250×140 ниже, над контейнерами', (560, 560, 810, 700), 3),
    ('B4 · 220×124 на тёмной стене у арки', (300, 470, 520, 594), 3),
    ('B5 · 280×158 кирпич левее трубы', (640, 300, 920, 458), 3),
]
pad, caph, hdr, gap = 20, 40, 76, 8
cw, rh = src.width, src.height
H = hdr + len(places) * (rh + caph + gap) + pad
canvas = Image.new('RGB', (cw + 2 * pad, H), (13, 14, 19)); d = ImageDraw.Draw(canvas)
d.text((pad, 14), '«ЗАРЯНКА» · S1 — где рисовать мелом (выбрать чистое место, не на окно/трубу/фигуру)',
       font=ImageFont.truetype(LATO_B, 25), fill=(226, 186, 104))
y = hdr
for cap, box, wd in places:
    r = put(src, box, wd)
    canvas.paste(r, (pad, y)); d.rectangle([pad, y, pad + cw, y + rh], outline=(60, 62, 74))
    d.text((pad + 4, y + rh + 6), cap, font=ImageFont.truetype(LATO_B, 20), fill=(240, 236, 228))
    y += rh + caph + gap
canvas.save(OUT)
print('saved', os.path.relpath(OUT, HERE), canvas.size)
