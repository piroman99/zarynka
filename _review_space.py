# -*- coding: utf-8 -*-
"""Контактный лист: новый космический арт + исправленная приёмная (+ старое для сравнения)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")
os.makedirs(OUT, exist_ok=True)


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def fit(im, w, h):
    im = im.convert("RGB")
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)


cells = [
    ("space_ship",   os.path.join(HERE, "assets/gen/ok_space_ship_0.jpg")),
    ("space_station",os.path.join(HERE, "assets/gen/ok_space_station_0.jpg")),
    ("kate_suit",    os.path.join(HERE, "assets/gen/ok_kate_suit_0.jpg")),
    ("reception_fix (БЕЗ англ.)", os.path.join(HERE, "assets/gen/ok_reception_fix_0.jpg")),
    ("БЫЛО: fxseries c1 (англ. табличка)", os.path.join(HERE, "assets/gen/fxseries_c1_enters_0.jpg")),
]

CW, CH, PAD, LBL = 620, 470, 16, 34
cols, rows = 2, 3
W = cols * CW + (cols + 1) * PAD
H = rows * (CH + LBL) + (rows + 1) * PAD
sheet = Image.new("RGB", (W, H), (24, 26, 32))
d = ImageDraw.Draw(sheet)
f = font(22)

for i, (title, path) in enumerate(cells):
    r, c = divmod(i, cols)
    x = PAD + c * (CW + PAD)
    y = PAD + r * (CH + LBL + PAD)
    d.text((x, y), f"{i+1}. {title}", fill=(235, 232, 226), font=f)
    if os.path.exists(path):
        im = fit(Image.open(path), CW, CH)
        sheet.paste(im, (x + (CW - im.width) // 2, y + LBL + (CH - im.height) // 2))

out = os.path.join(OUT, "review_14_spacegen.png")
sheet.save(out)
print("saved", os.path.relpath(out, HERE), sheet.size)
