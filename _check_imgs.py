# -*- coding: utf-8 -*-
"""Быстрая проверка, что сгенерированные кадры не пустые/битые."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for name in ("assets/gen/kate_reception_vn_0.png", "assets/gen/zaryanka_ref_0.png",
             "assets/review/review_01_style.png"):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        print("MISSING", name); continue
    im = Image.open(p).convert("RGB")
    w, h = im.size
    px = list(im.resize((60, 60)).getdata())
    mean = tuple(round(sum(c[i] for c in px) / len(px)) for i in range(3))
    uniq = len(set(px))
    print(f"{os.path.basename(name):32s} {w}x{h} mean={mean} uniq={uniq} {os.path.getsize(p)//1024}KB")
