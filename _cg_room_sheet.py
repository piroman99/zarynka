# -*- coding: utf-8 -*-
"""Лист: CG в НАШЕЙ приёмной (3 ракурса сверху) + пиковые CG."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "_sat")
os.makedirs(OUT, exist_ok=True)

items = [
    ("A · сверху-сбоку, через стол", "cg_room_a__gpt-image-2_0.png"),
    ("B · сверху-сбоку, ближе", "cg_room_b__gpt-image-2_0.png"),
    ("C · сверху и сзади-сбоку", "cg_room_c__gpt-image-2_0.png"),
    ("P4 · отказ, Сергей отвёл взгляд", "cg_p4_refusal__gpt-image-2_0.png"),
    ("P3 · «спасибо», крупный план", "cg_p3_thanks__gpt-image-2_0.png"),
    ("P2 · протягивает документы", "cg_p2_papers__gpt-image-2_0.png"),
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
d.text((pad, 14), "Зарянка · CG в НАШЕЙ приёмной (фон pilot_reception) — gpt-image-2",
       fill=(240, 240, 245), font=f)
for i, (lab, fn) in enumerate(items):
    c, r = i % cols, i // cols
    x = pad + c * (cw + pad)
    y = top + r * (ch + pad + 26)
    p = os.path.join(GEN, fn)
    if not os.path.exists(p):
        d.text((x + 10, y + 10), "нет: " + fn, fill=(220, 120, 120), font=fl)
        continue
    im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (x, y))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((x, y + ch + 5), lab, fill=(212, 216, 224), font=fl)
out = os.path.join(OUT, "cg_room_sheet.png")
cv.save(out)
print("saved", out, cv.size)
