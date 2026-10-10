# -*- coding: utf-8 -*-
"""Сводка-пруф: локальная обложка vs живая из ВК (обе 1920x768), + MAE."""
import os, sys, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vk

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, "assets", "review"); os.makedirs(REV, exist_ok=True)
local = os.path.join(HERE, "assets", "vk", "cover_b.png")
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

g = vk.call("groups.getById", group_id=vk.whoami()["id"], fields="cover")
g = g["groups"][0] if isinstance(g, dict) else g
big = max(g["cover"]["images"], key=lambda i: i["width"] * i["height"])
live_p = os.path.join(HERE, "assets", "vk", "_live_cover.png")
urllib.request.urlretrieve(big["url"], live_p)

W = 1280
def fit(p):
    im = Image.open(p).convert("RGB")
    return im.resize((W, round(W * im.height / im.width)), Image.LANCZOS)

a, b = fit(local), fit(live_p)
mae = round(float(np.abs(np.asarray(a, np.float32) - np.asarray(b.resize((W, a.height)), np.float32)).mean()), 2)

pad, head = 24, 46
canvas = Image.new("RGB", (W + 2 * pad, pad + head + a.height + head + b.height + pad), (24, 26, 30))
d = ImageDraw.Draw(canvas)
fb = ImageFont.truetype(F, 26)
y = pad
d.text((pad, y), "локально: assets/vk/cover_b.png (1920x768)", font=fb, fill=(240, 233, 219)); y += head
canvas.paste(a, (pad, y)); y += a.height
d.text((pad, y), f"в ВК сейчас (снято через API)  |  MAE = {mae}", font=fb, fill=(120, 220, 140)); y += head
canvas.paste(b, (pad, y))
out = os.path.join(REV, "review_21_vk_cover_fix.png")
canvas.save(out)
print("saved", out, "MAE", mae)
