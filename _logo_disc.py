# -*- coding: utf-8 -*-
"""Найти точный диск в logo_b_0.jpg (немаркий фон 255 -> кремовый диск)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "assets", "gen", "logo_b_0.jpg")
im = Image.open(p).convert("RGB")
a = np.asarray(im).astype(np.int16)
h, w, _ = a.shape
# «не белый» = хотя бы один канал заметно ниже 250
nz = (a.min(axis=2) < 246)
ys, xs = np.nonzero(nz)
print("bbox", xs.min(), ys.min(), xs.max(), ys.max())
print("center", (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2)
print("diam", xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
# горизонтальный срез через центр
cy = (ys.min() + ys.max()) // 2
row = a[cy]
lum = row.mean(axis=1)
print("row lum 0..40:", [int(v) for v in lum[:40]])
print("row lum 100..180:", [int(v) for v in lum[100:180:4]])
# цвет диска у края и в середине
cx = (xs.min() + xs.max()) // 2
for rad in (0, 100, 200, 300, 360, 380, 400, 420, 440, 460):
    y, x = cy, cx + rad
    if x < w:
        print("r=", rad, tuple(int(v) for v in a[y, x]))
