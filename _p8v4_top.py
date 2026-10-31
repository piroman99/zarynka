# -*- coding: utf-8 -*-
"""Кроп верхней части кадров p8 v4 (корпус корабля у верха) — проверка букв."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(HERE, "assets", "gen")
S = os.path.join(HERE, "_sat")

BOX = (0.45, 0.02, 1.00, 0.42)
for tag, name in (("A", "prolog_p8v4_a__gpt-image-2_0.png"),
                  ("B", "prolog_p8v4_b__gpt-image-2_0.png")):
    im = Image.open(os.path.join(G, name)).convert("RGB")
    w, h = im.size
    bx = (int(w * BOX[0]), int(h * BOX[1]), int(w * BOX[2]), int(h * BOX[3]))
    c = im.crop(bx)
    cw = 1100
    ch = int(round(cw * c.size[1] / c.size[0]))
    c = c.resize((cw, ch), Image.LANCZOS)
    p = os.path.join(S, "p8v4_top_%s.jpg" % tag)
    c.save(p, quality=92)
    print(p, c.size)