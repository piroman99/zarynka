# -*- coding: utf-8 -*-
"""Посмотреть starik_0.jpg + замерить фон (для вырезания)."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'review')
os.makedirs(OUT, exist_ok=True)

src = Image.open(os.path.join(HERE, 'assets', 'gen', 'starik_0.jpg')).convert('RGB')
w, h = src.size
print('size', w, h)
for pt in [(5, 5), (w - 5, 5), (5, h - 5), (w - 5, h - 5), (w // 2, 5), (w // 2, h - 5)]:
    print('  bg', pt, src.getpixel(pt))

v = src.copy()
v.thumbnail((640, 860))
p = os.path.join(OUT, 'review_130_starik_raw.png')
v.save(p)
print('->', os.path.relpath(p, HERE), v.size)
