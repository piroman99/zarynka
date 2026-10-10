# -*- coding: utf-8 -*-
"""Контактный лист партии-2: новые космические кадры + Екатерина в скафандре."""
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
    ("x_ship_dock — стыковка у Луны", "ok_x_ship_dock_0.jpg"),
    ("x_station_hall — зал под куполом", "ok_x_station_hall_0.jpg"),
    ("x_kate_moon — Зарянка на Луне", "ok_x_kate_moon_0.jpg"),
    ("x_kate_cockpit — Зарянка в кабине", "ok_x_kate_cockpit_0.jpg"),
]
CW, CH, PAD, LBL = 640, 480, 18, 36
cols, rows = 2, 2
W = cols * CW + (cols + 1) * PAD
Hh = rows * (CH + LBL) + (rows + 1) * PAD
sheet = Image.new("RGB", (W, Hh), (24, 26, 32))
d = ImageDraw.Draw(sheet)
f = font(23)
for i, (title, fn) in enumerate(cells):
    r, c = divmod(i, cols)
    x = PAD + c * (CW + PAD)
    y = PAD + r * (CH + LBL + PAD)
    d.text((x, y), f"{i+1}. {title}", fill=(235, 232, 226), font=f)
    p = os.path.join(HERE, "assets/gen", fn)
    if os.path.exists(p):
        im = fit(Image.open(p), CW, CH)
        sheet.paste(im, (x + (CW - im.width) // 2, y + LBL + (CH - im.height) // 2))
out = os.path.join(OUT, "review_16_space2.png")
sheet.save(out)
print("saved", os.path.relpath(out, HERE), sheet.size)
