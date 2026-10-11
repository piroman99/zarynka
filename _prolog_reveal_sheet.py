# -*- coding: utf-8 -*-
"""Лист «до/после появления по фразе»."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "assets", "review", "prolog_draft")
OUT = os.path.join(HERE, "assets", "review", "review_56_prolog_reveal.png")
G = "/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf"
L = "/usr/share/fonts/truetype/lato/Lato-Bold.ttf"
PAIRS = [
    ("v3_t35.0.png", "v3_t37.0.png", "S3 · до фразы «Марс — дело общее» → после"),
    ("v3_t66.0.png", "v3_t69.0.png", "S5 · до «Верховного Совета» → после"),
]
CW, CH = 900, 506
M, H, C = 18, 64, 40
rows = []
canvas = None
imgs = []
for a, b, cap in PAIRS:
    ia = Image.open(os.path.join(D, a)).resize((CW, CH), Image.LANCZOS)
    ib = Image.open(os.path.join(D, b)).resize((CW, CH), Image.LANCZOS)
    imgs.append((ia, ib, cap))
W = 2 * CW + 3 * M
Hh = H + len(imgs) * (CH + C + M)
canvas = Image.new("RGB", (W, Hh), (12, 13, 18))
d = ImageDraw.Draw(canvas)
d.text((M, 18), "«ЗАРЯНКА» — пролог v3: элементы появляются ПО ФРАЗЕ", font=ImageFont.truetype(G, 30), fill=(226, 186, 104))
y = H
for ia, ib, cap in imgs:
    canvas.paste(ia, (M, y)); canvas.paste(ib, (2 * M + CW, y))
    d.rectangle([M, y, M + CW, y + CH], outline=(60, 64, 80), width=2)
    d.rectangle([2 * M + CW, y, 2 * M + 2 * CW, y + CH], outline=(200, 160, 90), width=2)
    d.text((M, y + CH + 8), cap, font=ImageFont.truetype(L, 26), fill=(235, 232, 226))
    y += CH + C + M
canvas.save(OUT)
print("saved", os.path.relpath(OUT, HERE), canvas.size)
