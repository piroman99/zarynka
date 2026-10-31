# -*- coding: utf-8 -*-
"""Проверка: в сборку попал именно A (один ряд иллюминаторов), а не B."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
G = lambda p: os.path.join(HERE, p)
def stat(p):
    im = Image.open(p).convert("RGB").resize((320, 180))
    a = np.asarray(im, np.float32)
    return a.mean(axis=(0, 1))

for name, p in [("A gen", "assets/gen/prolog_p8v4_a__gpt-image-2_0.png"),
                ("B gen", "assets/gen/prolog_p8v4_b__gpt-image-2_0.png"),
                ("final p8", "assets/final/prolog/p8.png"),
                ("built webp", "vn2/img/prolog/p8.webp")]:
    m = stat(G(p))
    print("%-12s %6.1f %6.1f %6.1f  mean=%5.1f" % (name, m[0], m[1], m[2], m.mean()))
