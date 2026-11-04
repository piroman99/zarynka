# -*- coding: utf-8 -*-
"""Контактный лист новых CG: 3 верхних ракурса + 3 прямых."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "_sat")

items = [
    ("A · сверху-сбоку, через стол", "cg_top_a__gpt-image-2_0.png"),
    ("B · почти вертикально сверху", "cg_top_b__gpt-image-2_0.png"),
    ("C · сверху и сзади-сбоку", "cg_top_c__gpt-image-2_0.png"),
    ("D · прямо, куратор в расфокусе", "cg_sad_a__gpt-image-2_0.png"),
    ("E · прямо, средний план", "cg_sad_b__gpt-image-2_0.png"),
    ("F · из-за плеча куратора", "cg_sad_c__gpt-image-2_0.png"),
]
cw, ch, cols = 640, 360, 2
rows = (len(items) + cols - 1) // cols
pad, top = 16, 52
W = pad + cols * (cw + pad)
H = top + rows * (ch + pad + 26) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except Exception:
    f = fl = ImageFont.load_default()
d.text((pad, 14), "Зарянка · CG «сникшая Екатерина» — новые кадры 16:9 (gpt-image-2)",
       fill=(240, 240, 245), font=f)
for i, (lab, fn) in enumerate(items):
    c, r = i % cols, i // cols
    x = pad + c * (cw + pad)
    y = top + r * (ch + pad + 26)
    im = Image.open(os.path.join(GEN, fn)).convert("RGB").resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (x, y))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((x, y + ch + 5), lab, fill=(212, 216, 224), font=fl)
out = os.path.join(OUT, "cg_new_sheet.png")
cv.save(out)
print("saved", out, cv.size)
