# -*- coding: utf-8 -*-
"""Сводный лист экранов VN-прототипа (2x2)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "_shots_vn")
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
names = [("01_title.png", "Тайтл (PWA)"), ("02_kate_dialog.png", "Диалог · приёмная"),
         ("03_alley.png", "Диалог · аллея"), ("04_end.png", "Финал эпизода 1")]
ims = [Image.open(os.path.join(S, n)).convert("RGB") for n, _ in names]
W, H = ims[0].size
tw = 640
th = round(tw * H / W)
pad, head = 18, 34
cols, rows = 2, 2
cw, chh = tw * cols + pad * (cols + 1), (th + head) * rows + pad * (rows + 1)
sheet = Image.new("RGB", (cw, chh), (18, 20, 24))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype(F, 20)
for i, (im, (_, lab)) in enumerate(zip(ims, names)):
    r, c = divmod(i, cols)
    x = pad + c * (tw + pad)
    y = pad + r * (th + head + pad)
    d.text((x, y), lab, font=f, fill=(240, 233, 219))
    sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + head))
out = os.path.join(HERE, "assets", "review", "review_22_vn_prototype.png")
sheet.save(out)
print("saved", out, sheet.size)
