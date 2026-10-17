# -*- coding: utf-8 -*-
"""Углы/центр логотипов: какой годится в круг."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for n in ("logo_a_0.jpg", "logo_b_0.jpg"):
    im = Image.open(os.path.join(HERE, "assets", "gen", n)).convert("RGB")
    w, h = im.size
    pts = {"tl": (2, 2), "tr": (w - 3, 2), "bl": (2, h - 3), "br": (w - 3, h - 3),
           "mid-top": (w // 2, 3), "mid-left": (3, h // 2), "center": (w // 2, h // 2)}
    print(n, im.size, {k: im.getpixel(v) for k, v in pts.items()})
