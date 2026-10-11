# -*- coding: utf-8 -*-
"""Контактный лист черновых кадров пролога."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "mock", "prolog")
REV = os.path.join(HERE, "assets", "review")
G = "/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf"
L = "/usr/share/fonts/truetype/lato/Lato-Medium.ttf"
PW, PH = 620, 349
c, r = 3, 2
M, H = 18, 60
names = [("s1", "S1 · подворотня"), ("s2", "S2 · Космодром (ракета)"), ("s3", "S3 · «а обычных людей нет?»"),
         ("s4", "S4 · слепленный ролик"), ("s5", "S5 · лозунг облетел страну"), ("s6", "S6 · очередь")]
W = c * PW + (c + 1) * M
Hh = H + r * PH + (r + 1) * M
sh = Image.new("RGB", (W, Hh), (12, 12, 16))
d = ImageDraw.Draw(sh)
d.text((M, 16), "«ЗАРЯНКА» — пролог: черновые кадры (кадры-моки, 0 ₽)", font=ImageFont.truetype(G, 26), fill=(255, 200, 120))
for i, (n, lbl) in enumerate(names):
    im = Image.open(os.path.join(SRC, n + "_base.png")).resize((PW, PH), Image.LANCZOS)
    x = M + (i % c) * (PW + M); y = H + M + (i // c) * (PH + M)
    sh.paste(im, (x, y))
    d.rectangle([x, y, x + PW, y + PH], outline=(70, 74, 90), width=2)
    d.text((x + 8, y + PH + 4), lbl, font=ImageFont.truetype(L, 20), fill=(220, 224, 235))
os.makedirs(REV, exist_ok=True)
p = os.path.join(REV, "review_54_prolog_frames.png")
sh.save(p)
print("saved", os.path.relpath(p, HERE), sh.size)
