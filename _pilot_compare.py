# -*- coding: utf-8 -*-
"""Лист сравнения: 2016 спрайт (авторский) | прежний GPT-образец | пилот «акварельный космос»."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
items = [
    ("2016: авторский спрайт", "assets/src/caccf3b4ebc5.png"),
    ("было: GPT (комбинезон)", "assets/sprites/kate_overalls.png"),
    ("пилот: акварель, POV Сергея", "assets/pilot/pilot_s_enter_0.png"),
]

H = 620
tiles = []
for cap, rel in items:
    p = os.path.join(HERE, rel)
    im = Image.open(p).convert("RGB")
    w = round(im.width * H / im.height)
    tiles.append((cap, im.resize((w, H), Image.LANCZOS)))

pad = 16
W = sum(t[1].width for t in tiles) + pad * (len(tiles) + 1)
sheet = Image.new("RGB", (W, H + 60), (24, 24, 28))
x = pad
from PIL import ImageDraw
d = ImageDraw.Draw(sheet)
for cap, im in tiles:
    sheet.paste(im, (x, 44))
    d.text((x, 16), cap, fill=(235, 235, 235))
    x += im.width + pad

out = os.path.join(HERE, "assets", "pilot", "compare.png")
sheet.save(out)
print(out, sheet.size)
for cap, rel in items:
    im = Image.open(os.path.join(HERE, rel))
    print(" ", rel, im.size)
