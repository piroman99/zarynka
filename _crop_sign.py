# -*- coding: utf-8 -*-
"""Вырезать верхнюю область стены reception_fix, чтобы проверить, нет ли латинской таблички."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
for nm in ("ok_reception_fix_0.jpg", "fxseries_c1_enters_0.jpg"):
    p = os.path.join(HERE, "assets/gen", nm)
    im = Image.open(p).convert("RGB")
    W, H = im.size
    crop = im.crop((int(W*0.35), 0, W, int(H*0.45)))  # верх-право, где была табличка
    crop = crop.resize((crop.width*2, crop.height*2), Image.LANCZOS)
    out = os.path.join(HERE, ".tmp_diag", "wall_" + nm.replace(".jpg", ".png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    crop.save(out)
    print("saved", os.path.relpath(out, HERE), crop.size)
