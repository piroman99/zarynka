# -*- coding: utf-8 -*-
"""Сверка: утверждённая Екатерина vs попытки её ПОВТОРИТЬ (i2i) + грубая метрика схожести."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")
REF = os.path.join(HERE, "assets", "gen", "kate_overalls_0.png")


def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    if not os.path.exists(p):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def mae(path):
    a = np.asarray(Image.open(REF).convert("RGB").resize((256, 256)), dtype=np.int16)
    b = np.asarray(Image.open(path).convert("RGB").resize((256, 256)), dtype=np.int16)
    return float(np.abs(a - b).mean())


items = [
    ("УТВЕРЖДЕНО: Екатерина (gpt-image-2)", "assets/gen/kate_overalls_0.png", None),
    ("Спрайт-вырезка (эталон для i2i)", "assets/sprites/kate_overalls.png", None),
    ("flux-2 i2i: повтор", "assets/gen/kate_repro__flux-2_0.jpg", True),
    ("nano-banana-2.1 i2i: повтор", "assets/gen/kate_repro__nano-banana-2.1_0.jpg", True),
    ("grok-imagine i2i: повтор", "assets/gen/kate_repro__grok-imagine_0.jpg", True),
    ("flux-2 по тексту (было иначе)", "assets/gen/flux2_kate_0.jpg", True),
    ("2016 спрайт (самый первый)", "assets/orig/za smile.png", True),
]
cell = (430, 580)
cols = 4
pad, top = 16, 54
rows = (len(items) + cols - 1) // cols
W = pad + cols * (cell[0] + pad)
H = top + rows * (cell[1] + pad + 30) + pad
cv = Image.new("RGB", (W, H), (18, 20, 26))
d = ImageDraw.Draw(cv)
d.text((pad, 14), "Екатерина — можно ли повторить утверждённый образ? (MAE↓ = ближе к эталону)",
       fill=(240, 240, 245), font=font(22, True))
for i, (lab, rel, score) in enumerate(items):
    c, r = i % cols, i // cols
    x = pad + c * (cell[0] + pad)
    y = top + r * (cell[1] + pad + 30)
    d.rectangle([x, y, x + cell[0], y + cell[1]], fill=(38, 40, 48))
    p = os.path.join(HERE, rel)
    if os.path.exists(p):
        im = fit(Image.open(p), cell)
        cv.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
        if score:
            lab = f"{lab}  ·  MAE {mae(p):.1f}"
    d.text((x, y + cell[1] + 6), lab, fill=(212, 216, 224), font=font(14))

o = os.path.join(OUT, "review_08_kate_repro.png")
cv.save(o)
print("saved", o, cv.size)
