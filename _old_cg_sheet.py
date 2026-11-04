# -*- coding: utf-8 -*-
"""Лист: старые отвергнутые CG «сникшая Екатерина в кресле» (10 окт)."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "_sat")
os.makedirs(OUT, exist_ok=True)

items = [
    ("nano-banana-2.1 · c4_sits", "series_c4_sits_0.jpg"),
    ("nano-banana-2.1 · c5_sad", "series_c5_sad_0.jpg"),
    ("flux-2 · c4_sits", "fxseries_c4_sits_0.jpg"),
    ("flux-2 · c5_sad", "fxseries_c5_sad_0.jpg"),
]
cw, ch = 460, 620
pad, top = 18, 54
cols = 4
W = pad + cols * (cw + pad)
H = top + ch + 40
cv = Image.new("RGB", (W, H), (16, 18, 24))
d = ImageDraw.Draw(cv)
try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except Exception:
    f = fl = ImageFont.load_default()
d.text((pad, 16), "Отвергнутые CG от 10 окт: Екатерина в кресле", fill=(240, 240, 245), font=f)
for i, (lab, fn) in enumerate(items):
    p = os.path.join(GEN, fn)
    im = Image.open(p).convert("RGB")
    r = min(cw / im.width, ch / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    x = pad + i * (cw + pad)
    cv.paste(im, (x + (cw - im.width) // 2, top))
    d.text((x, top + ch + 8), lab, fill=(212, 216, 224), font=fl)
cv.save(os.path.join(OUT, "old_cg_sad.png"))
print("saved", os.path.join(OUT, "old_cg_sad.png"), cv.size)
