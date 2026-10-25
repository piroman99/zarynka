# -*- coding: utf-8 -*-
"""Лист Ивану: кадр p6 в движке (2 страницы) + переход на s2."""
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
    ("p6 · страница 1 — «Вторая Марсианская экспедиция… Один раз были?»", "p6_p6_p0.png"),
    ("p6 · страница 2 — «Ну и хорошо, гнаться за третьей…»", "p6_p6_p1.png"),
    ("переход на s2 · «Но экспедиция потихоньку набиралась…» (цех)", "p6_s2_after.png"),
]

cw, pad, top, lab = 1200, 16, 56, 28
first = Image.open(os.path.join(S, items[0][1]))
ch = int(round(cw * first.size[1] / first.size[0]))
W = cw + 2 * pad
H = top + len(items) * (ch + lab + pad) + pad
cv = Image.new("RGB", (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
d.text((pad, 16), "Зарянка · кадр p6 «хроника первого полёта» в движке (вариант B)",
       fill=(240, 240, 245), font=f)
y = top
for labt, name in items:
    p = os.path.join(S, name)
    im = Image.open(p).convert("RGB")
    # скриншот 1600×900 — режем по stage, если файл больше
    if im.size[0] != 1600:
        pass
    im = im.resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 4), labt, fill=(212, 216, 224), font=fl)
    y += ch + lab + pad
out = os.path.join(S, "sheet_p6_vn.png")
cv.save(out)
print("saved", out, cv.size)

w2 = 820
im = cv.resize((w2, int(round(w2 * cv.size[1] / cv.size[0]))), Image.LANCZOS)
dst = os.path.join(S, "sheet_p6_vn_small.jpg")
im.save(dst, quality=88)
print("saved", dst, im.size)
