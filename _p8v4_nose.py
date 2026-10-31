# -*- coding: utf-8 -*-
"""Тесные кропы носа корабля в нативном разрешении — проверить буквы на корпусе/стекле."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, "assets", "gen")
S = os.path.join(HERE, "_sat")

try:
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    fl = ImageFont.load_default()

JOBS = [("A", "prolog_p8v4_a__gpt-image-2_0.png"), ("B", "prolog_p8v4_b__gpt-image-2_0.png")]
# нос корабля примерно в правой-нижней части кадра
BOX = (0.45, 0.55, 1.00, 1.00)

rows = []
for tag, name in JOBS:
    im = Image.open(os.path.join(G, name)).convert("RGB")
    w, h = im.size
    c = im.crop((int(w * BOX[0]), int(h * BOX[1]), int(w * BOX[2]), int(h * BOX[3])))
    rows.append((tag + " · нос, 100% натив", c))

cw = 1000
pad, top, lab = 14, 52, 26
H = top + sum(int(round(cw * c.size[1] / c.size[0])) + lab + pad for _, c in rows) + pad
cv = Image.new("RGB", (cw + 2 * pad, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 14), "p8 v4 · нос корабля, кроп 1:1 (ищем буквы)", fill=(240, 240, 245), font=fl)
y = top
for labt, c in rows:
    ch = int(round(cw * c.size[1] / c.size[0]))
    cv.paste(c.resize((cw, ch), Image.LANCZOS), (pad, y))
    d.text((pad, y + ch + 4), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad
out = os.path.join(S, "p8v4_nose.png")
cv.save(out)
print("saved", out, cv.size)
im = cv.resize((760, int(round(760 * cv.size[1] / cv.size[0]))), Image.LANCZOS)
p = os.path.join(S, "p8v4_nose_small.jpg")
im.save(p, quality=90)
print("saved", p, im.size)