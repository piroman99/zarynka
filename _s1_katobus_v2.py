# -*- coding: utf-8 -*-
"""S1: котобус мелом на финальной плашке — НАБОР вариантов размещения.
A — как есть.  B — плоско (наклейкой, как раньше).  C..F — на плоскости стены
(перспективный варп + screen-блендинг: мел светлеет по рельефу).
Выход: assets/review/review_84_s1_katobus_v2.png. Кадры vn2 НЕ трогаем.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'vn2', 'img', 'prolog', 's1.png')
OUT = os.path.join(HERE, 'assets', 'review', 'review_84_s1_katobus_v2.png')
LATO_B = '/usr/share/fonts/truetype/lato/Lato-Bold.ttf'
CHALK = (240, 236, 222)


def draw_katobus(w, h, wd=4):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    C = CHALK + (255,)
    x0, y0, x1, y1 = 6, 46, w - 78, h - 46
    d.rounded_rectangle([x0, y0, x1, y1], radius=int((y1 - y0) * 0.35), outline=C, width=wd)
    d.polygon([(x0 + 34, y0 + 4), (x0 + 62, y0 - 34), (x0 + 90, y0 + 4)], outline=C, width=wd)
    d.polygon([(x1 - 90, y0 + 4), (x1 - 62, y0 - 34), (x1 - 34, y0 + 4)], outline=C, width=wd)
    for wx in range(x0 + 26, x1 - 30, 46):
        d.rectangle([wx, y0 + 20, wx + 28, y0 + 54], outline=C, width=wd)
    for lx in range(x0 + 22, x1 - 18, 40):
        d.line([(lx, y1), (lx, y1 + 32)], fill=C, width=wd)
    d.line([(x1 - 2, y0 + 62), (x1 + 42, y0 + 46), (x1 + 54, y0 + 88)], fill=C, width=wd)
    d.ellipse([x1 - 60, y0 + 24, x1 - 44, y0 + 40], outline=C, width=3)
    for k in range(3):
        d.line([(x1 - 58, y0 + 46 + k * 9), (x1 - 8, y0 + 38 + k * 11)], fill=C, width=2)
    return im


def find_coeffs(pa, pb):
    m = []
    for p1, p2 in zip(pa, pb):
        m.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        m.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(m, float); B = np.array(pb, float).reshape(8)
    return np.linalg.solve(A.T @ A, A.T @ B).reshape(8)


def flat(base, box, a=155):
    x0, y0, x1, y1 = box
    ch = draw_katobus(x1 - x0, y1 - y0).filter(ImageFilter.GaussianBlur(0.6))
    ch.putalpha(ch.split()[3].point(lambda v: int(v * a / 255)))
    out = base.convert('RGBA'); out.paste(ch, (x0, y0), ch)
    return out.convert('RGB')


def painted(base, quad, a=205, blur=0.9):
    """Рисунок вписан в quad (TL,TR,BR,BL) с перспективой; screen-блендинг по свету."""
    SRC_W, SRC_H = 470, 190
    src = draw_katobus(SRC_W + 90, SRC_H)          # запас под хвост справа
    box = [(6, 46), (SRC_W - 78, 46), (SRC_W - 78, SRC_H - 46), (6, SRC_H - 46)]
    coeffs = find_coeffs(quad, box)
    warped = src.transform(base.size, Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC)
    warped = warped.filter(ImageFilter.GaussianBlur(blur))
    alpha = warped.split()[3].point(lambda v: int(v * a / 255))
    chalk_rgb = Image.new('RGB', base.size, CHALK)
    masked = Image.composite(chalk_rgb, Image.new('RGB', base.size, (0, 0, 0)), alpha)
    return ImageChops.screen(base.convert('RGB'), masked)


src = Image.open(P).convert('RGB')
print('s1', src.size)
panels = [('A · как есть (без пасхалки)', src)]
panels.append(('B · плоско, наклейкой (плоскости НЕ совпадают)', flat(src, (150, 620, 470, 800))))
panels.append(('C · по плоскости: тёмная стена у арки', painted(src, [(168, 600), (470, 636), (470, 812), (168, 764)])))
panels.append(('D · по плоскости: освещённая кирпичная стена', painted(src, [(880, 255), (1230, 300), (1230, 600), (880, 505)])))
panels.append(('E · по плоскости: стена ниже, ближе к свету', painted(src, [(950, 330), (1360, 362), (1360, 700), (950, 648)])))
panels.append(('F · по плоскости: правая тёмная стена', painted(src, [(1500, 300), (1860, 344), (1860, 648), (1500, 586)])))

pad, caph, hdr, gap = 20, 44, 82, 10
cw = src.width
rh = round(src.height * cw / src.width)
H = hdr + len(panels) * (rh + caph + gap) + pad
canvas = Image.new('RGB', (cw + 2 * pad, H), (13, 14, 19))
d = ImageDraw.Draw(canvas)
d.text((pad, 16), '«ЗАРЯНКА» · S1 — котобус мелом: варианты размещения (A как есть / B наклейкой / C–F по плоскости стены)',
       font=ImageFont.truetype(LATO_B, 26), fill=(226, 186, 104))
y = hdr
for cap, im in panels:
    r = im.resize((cw, rh), Image.LANCZOS)
    canvas.paste(r, (pad, y)); d.rectangle([pad, y, pad + cw, y + rh], outline=(60, 62, 74))
    d.text((pad + 4, y + rh + 7), cap, font=ImageFont.truetype(LATO_B, 21), fill=(240, 236, 228))
    y += rh + caph + gap
canvas.save(OUT)
print('saved', os.path.relpath(OUT, HERE), canvas.size)
