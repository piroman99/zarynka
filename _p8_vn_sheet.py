# -*- coding: utf-8 -*-
"""Лист Ивану: p8 «гидролаборатория» в движке (между p7 и s3)."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(HERE, "_sat")

try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    fl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    f = fl = ImageFont.load_default()

items = [
    ("p7 · «Но экспедиция потихоньку набиралась, модули корабля строились…» (цех)", "p8_p7_last.png"),
    ("p8 · «Космонавты начали тренировки, утверждалась научная программа…» (гидролаборатория)", "p8_p8_p0.png"),
    ("s3 · «Пока тот самый умник не спросил: „Марс — дело общее?“»", "p8_s3_p0.png"),
]

cw, pad, top, lab = 1200, 16, 56, 28
first = Image.open(os.path.join(S, items[0][1]))
ch = int(round(cw * first.size[1] / first.size[0]))
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 16), "Зарянка · кадр p8 «гидролаборатория» в движке (s1 → p6 → p7 → p8 → s3)",
       fill=(240, 240, 245), font=f)
y = top
for labt, name in items:
    im = Image.open(os.path.join(S, name)).convert("RGB")
    im = im.resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 4), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad
out = os.path.join(S, "sheet_p8_vn.png")
cv.save(out)
print("saved", out, cv.size)

w2 = 900
im = cv.resize((w2, int(round(w2 * cv.size[1] / cv.size[0]))), Image.LANCZOS)
dst = os.path.join(S, "sheet_p8_vn_small.jpg")
im.save(dst, quality=88)
print("saved", dst, im.size)