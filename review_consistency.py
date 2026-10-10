# -*- coding: utf-8 -*-
"""Лист: держит ли nano-banana одного персонажа в разных сценах.
Ряд 1 — референс. Ряд 2 — nano-banana-2. Ряд 3 — nano-banana-2.1.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "review")
REF = os.path.join(HERE, "assets", "gen", "kate_overalls_0.png")


def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def fit(im, box):
    im = im.convert("RGB")
    r = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def mae(path):
    a = np.asarray(Image.open(REF).convert("RGB").resize((256, 256)), dtype=np.int16)
    b = np.asarray(Image.open(path).convert("RGB").resize((256, 256)), dtype=np.int16)
    return float(np.abs(a - b).mean())


SCENES = ["s1_reception", "s2_window", "s3_chair"]
SLAB = ["приёмная (с папкой)", "у окна, задумчива", "в кресле, улыбается"]

rows = [
    ("ЭТАЛОН", None),
    ("nano-banana-2", "nanobanana2"),
    ("nano-banana-2.1", "nanobanana21"),
]
cell = (440, 600)
cols = 4
pad, top = 16, 60
W = pad + cols * (cell[0] + pad)
H = top + len(rows) * (cell[1] + pad + 30) + pad
cv = Image.new("RGB", (W, H), (18, 20, 26))
d = ImageDraw.Draw(cv)
d.text((pad, 14), "Один персонаж в разных сценах — nano-banana-2 vs 2.1 (MAE↓ = ближе к эталону)",
       fill=(240, 240, 245), font=font(24, True))

for r, (lab, tag) in enumerate(rows):
    y = top + r * (cell[1] + pad + 30)
    for c, (sc, slab) in enumerate(zip(SCENES, SLAB)):
        x = pad + c * (cell[0] + pad)
        d.rectangle([x, y, x + cell[0], y + cell[1]], fill=(38, 40, 48))
        rel = REF if tag is None else os.path.join("assets", "gen", f"consist_{tag}__{sc}_0.jpg")
        p = rel if os.path.isabs(rel) else os.path.join(HERE, rel)
        cap = f"{lab} · {slab}"
        if os.path.exists(p):
            im = fit(Image.open(p), cell)
            cv.paste(im, (x + (cell[0] - im.width) // 2, y + (cell[1] - im.height) // 2))
            if tag is not None:
                cap += f"  MAE {mae(p):.1f}"
        else:
            d.text((x + 12, y + 12), "нет файла", fill=(210, 120, 120), font=font(15))
        d.text((x, y + cell[1] + 6), cap, fill=(214, 218, 226), font=font(14))

o = os.path.join(OUT, "review_09_consistency.png")
cv.save(o)
print("saved", o, cv.size)
