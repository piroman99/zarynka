# -*- coding: utf-8 -*-
"""Контрольный лист по спрайтам персонажей."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")

def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def font(sz):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()

items = [
    ("Екатерина — комбинезон (Земля)", "assets/sprites/kate_overalls.png"),
    ("Екатерина — тревога/грусть", "assets/sprites/kate_sad.png"),
    ("Сергей (Лихнецкий)", "assets/sprites/sergey.png"),
    ("Эталон: кудри (канон)", "assets/gen/zaryanka_ref_curly_0.png"),
]
cell = (430, 620); cols = 4; pad, top = 16, 46
W = pad + cols * (cell[0] + pad); H = top + pad + (cell[1] + pad + 26)
cv = Image.new("RGB", (W, H), (24, 26, 32)); d = ImageDraw.Draw(cv)
d.text((pad, 12), "Зарянка — спрайты персонажей", fill=(240, 240, 245), font=font(22))
for i, (lab, rel) in enumerate(items):
    x = pad + i * (cell[0] + pad); y = top + pad
    d.rectangle([x, y, x + cell[0], y + cell[1]], fill=(40, 42, 50))
    p = os.path.join(HERE, rel)
    if os.path.exists(p):
        im = fit(Image.open(p), cell)
        cv.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
    d.text((x, y + cell[1] + 4), lab, fill=(210, 214, 222), font=font(15))
out = os.path.join(OUT, "review_03_sprites.png")
cv.save(out, "PNG"); print("saved", out, cv.size)
