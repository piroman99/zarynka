# -*- coding: utf-8 -*-
"""Проверка: есть ли латиница на стене в кадре приёмной (fix2) и в фоне кабинета."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, ".tmp_diag")
os.makedirs(D, exist_ok=True)
for nm, box in (("ok_reception_fix2_0.jpg", (0.30, 0.0, 1.0, 0.5)),
                ("ok_office_clean_0.jpg",  (0.0, 0.0, 1.0, 0.6))):
    p = os.path.join(HERE, "assets/gen", nm)
    im = Image.open(p).convert("RGB")
    W, H = im.size
    c = im.crop((int(W*box[0]), int(H*box[1]), int(W*box[2]), int(H*box[3])))
    c = c.resize((c.width*2, c.height*2), Image.LANCZOS)
    out = os.path.join(D, "wall2_" + nm.rsplit(".", 1)[0] + ".png")
    c.save(out)
    print("saved", os.path.relpath(out, HERE), c.size)
