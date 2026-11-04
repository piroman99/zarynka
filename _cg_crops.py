# -*- coding: utf-8 -*-
"""Кропы в нативном разрешении: лицо + поиск «букв» (мелкие тёмные штрихи на светлом)."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "assets", "gen")
OUT = os.path.join(HERE, "_sat")
os.makedirs(OUT, exist_ok=True)

JOBS = [
    ("cg_top_a__gpt-image-2_0.png", (0.30, 0.10, 0.72, 0.52), "top_a_face"),
    ("cg_top_b__gpt-image-2_0.png", (0.24, 0.16, 0.66, 0.58), "top_b_face"),
    ("cg_top_c__gpt-image-2_0.png", (0.44, 0.10, 0.86, 0.52), "top_c_face"),
    ("cg_sad_a__gpt-image-2_0.png", (0.20, 0.12, 0.62, 0.54), "sad_a_face"),
    ("cg_sad_b__gpt-image-2_0.png", (0.20, 0.12, 0.62, 0.54), "sad_b_face"),
    ("cg_sad_c__gpt-image-2_0.png", (0.10, 0.12, 0.52, 0.54), "sad_c_face"),
]
for fn, (x0, y0, x1, y1), tag in JOBS:
    p = os.path.join(GEN, fn)
    im = Image.open(p).convert("RGB")
    w, h = im.size
    box = (int(w * x0), int(h * y0), int(w * x1), int(h * y1))
    c = im.crop(box)
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    out = os.path.join(OUT, "crop_%s.png" % tag)
    c.save(out)
    print(tag, box, c.size, '->', out)
