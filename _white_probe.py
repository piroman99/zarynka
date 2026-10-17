# -*- coding: utf-8 -*-
"""Где в кадре-карточке есть чисто белое (>=250 по всем каналам)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for tag in ("big_card", "big_kate"):
    p = os.path.join(HERE, ".tmp_avmcheck", tag + ".png")
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.int16)
    m = a.min(axis=2) >= 250
    print(tag, "белых пикселей:", int(m.sum()))
    ys, xs = np.nonzero(m)
    if len(ys):
        print("  bbox", xs.min(), ys.min(), xs.max(), ys.max())
        # разброс по y
        print("  первые 12:", [(int(x), int(y)) for x, y in list(zip(xs, ys))[:12]])
        # гистограмма по вертикальным полосам
        import collections
        cnt = collections.Counter((y // 50) * 50 for y in ys)
        print("  по y (шаг 50):", dict(sorted(cnt.items())))
