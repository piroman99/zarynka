# -*- coding: utf-8 -*-
"""Где золотой текст чипа в ЖИВОМ рендере: узкая полоса y 840..915, строгий отбор
по цвету (255,210,120), ищем только в зоне x 300..1800."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
E = 2400.0
im = Image.open(os.path.join(HERE, '_sat', 's5b_on.png')).convert('RGB')
W, H = im.size
S = E / W
px = im.load()
pts = []
for y in range(int(830 / S), int(925 / S)):
    for x in range(int(300 / S), int(1900 / S)):
        r, g, b = px[x, y]
        if abs(r - 255) < 30 and abs(g - 210) < 30 and abs(b - 120) < 40:
            pts.append((x, y))
print('золотых пикселей:', len(pts))
if pts:
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    print('текст по факту: x %.0f..%.0f (центр %.0f, ширина %.0f)  y %.0f..%.0f'
          % (min(xs) * S, max(xs) * S, (min(xs) + max(xs)) / 2 * S,
             (max(xs) - min(xs)) * S, min(ys) * S, max(ys) * S))
    print('ожидание: x 609..1311 (центр 960, ширина 702), y ~852..898')
