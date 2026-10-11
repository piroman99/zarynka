# -*- coding: utf-8 -*-
"""Сравнительный лист: стиль финальных кадров пролога (кинохроника vs аниме)."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "assets", "review", "review_55_prolog_style.png")
LATO_B = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
GOTH = "/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf"

ITEMS = [
    ("assets/gen/prolog_s1_cin_0.jpg", "S1 · ПОДВОРОТНЯ — кинохроника"),
    ("assets/gen/prolog_s2_cin_0.jpg", "S2 · ЗВЁЗДНЫЙ ГОРОДОК — кинохроника"),
    ("assets/gen/prolog_s2_anime_0.jpg", "S2 · ЗВЁЗДНЫЙ ГОРОДОК — аниме-гальгэ (как VN)"),
]
CW = 900
imgs = []
for p, cap in ITEMS:
    im = Image.open(os.path.join(HERE, p)).convert("RGB")
    im = im.resize((CW, round(im.height * CW / im.width)), Image.LANCZOS)
    imgs.append((im, cap))

pad, cap_h, hdr = 18, 46, 70
total_h = hdr + sum(im.height + cap_h + pad for im, _ in imgs) + pad
canvas = Image.new("RGB", (CW + 2 * pad, total_h), (14, 15, 20))
d = ImageDraw.Draw(canvas)
d.text((pad, 18), "«ЗАРЯНКА» — пролог: стиль финальных кадров (flux-2)", font=ImageFont.truetype(GOTH, 30), fill=(226, 186, 104))
y = hdr
for im, cap in imgs:
    canvas.paste(im, (pad, y))
    y += im.height + 6
    d.text((pad, y), cap, font=ImageFont.truetype(LATO_B, 30), fill=(240, 236, 228))
    y += cap_h
canvas.save(OUT)
print("saved", os.path.relpath(OUT, HERE), canvas.size)
