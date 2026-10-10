# -*- coding: utf-8 -*-
"""Лист старого логотипа/иконок/меню из assets/orig (2016)."""
import os, glob
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")
os.makedirs(OUT, exist_ok=True)


def font(sz):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


items = []
for p in sorted(glob.glob(os.path.join(HERE, "assets", "orig", "*"))):
    if p.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
        items.append(os.path.relpath(p, HERE))

cell = (300, 300)
cols = 5
pad, top = 14, 44
rows = (len(items) + cols - 1) // cols
W = pad + cols * (cell[0] + pad)
H = top + rows * (cell[1] + pad + 24) + pad
cv = Image.new("RGB", (W, H), (18, 20, 26))
d = ImageDraw.Draw(cv)
d.text((pad, 12), "assets/orig — старый логотип/меню/иконки (2016)", fill=(240, 240, 245), font=font(20))
for i, rel in enumerate(items):
    c, r = i % cols, i // cols
    x = pad + c * (cell[0] + pad)
    y = top + r * (cell[1] + pad + 24)
    d.rectangle([x, y, x + cell[0], y + cell[1]], fill=(38, 40, 48))
    im = fit(Image.open(os.path.join(HERE, rel)), cell)
    cv.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
    d.text((x, y + cell[1] + 4), os.path.basename(rel), fill=(210, 214, 222), font=font(13))

o = os.path.join(OUT, "review_07_logo.png")
cv.save(o)
print("saved", o, cv.size)
