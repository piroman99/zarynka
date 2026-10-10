# -*- coding: utf-8 -*-
"""Контрольный лист: стиль flux-2 (выбор заказчика) на ключевых кадрах «Зарянки»."""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")
os.makedirs(OUT, exist_ok=True)


def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


items = [
    ("2016 спрайт — образец стиля", "assets/orig/za smile.png"),
    ("flux-2: Зарянка — эталон", "assets/gen/flux2_zaryanka_0.jpg"),
    ("flux-2: Зарянка — «попроще»", "assets/gen/flux2_zaryanka_simple_0.jpg"),
    ("flux-2: Сергей Лихнецкий (инженер)", "assets/gen/sergey_eng_old__flux-2_0.jpg"),
    ("flux-2: Екатерина (комбинезон)", "assets/gen/flux2_kate_0.jpg"),
    ("flux-2: фон — приёмная комиссия", "assets/gen/flux2_bg_reception_0.jpg"),
    ("gpt-image-2: Зарянка (для сверки)", "assets/gen/zaryanka_ref_0.png"),
    ("gpt-image-2: приёмная (для сверки)", "assets/gen/kate_reception_vn_0.png"),
]

COL, ROW = 4, 2
cell = (520, 700)
pad, top = 16, 52
W = pad + COL * (cell[0] + pad)
H = top + ROW * (cell[1] + pad + 26) + pad
cv = Image.new("RGB", (W, H), (18, 20, 26))
d = ImageDraw.Draw(cv)
d.text((pad, 14), "Zaryanka — стиль flux-2 (выбор заказчика)", fill=(240, 240, 245), font=font(24))
for i, (lab, rel) in enumerate(items):
    c, r = i % COL, i // COL
    x = pad + c * (cell[0] + pad)
    y = top + r * (cell[1] + pad + 26)
    d.rectangle([x, y, x + cell[0], y + cell[1]], fill=(38, 40, 48))
    p = os.path.join(HERE, rel)
    if os.path.exists(p):
        im = fit(Image.open(p), cell)
        cv.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
    else:
        d.text((x + 12, y + 12), "нет файла", fill=(200, 120, 120), font=font(15))
    d.text((x, y + cell[1] + 5), lab, fill=(212, 216, 224), font=font(15))

out = os.path.join(OUT, "review_06_flux2.png")
cv.save(out, "PNG")
print("saved", out, cv.size)
