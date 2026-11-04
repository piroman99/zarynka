# -*- coding: utf-8 -*-
"""Числовая проверка чипа кадра 12 (s5b): где реально тёмная плашка и где золотой текст.
Сверяем с заданным в _vn2_build.py: плашка (560,830,1360,920), текст (960,875) mm, GOLD 46."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
E = 2400.0
for name in ('demo_s5b.png',):
    im = Image.open(os.path.join(HERE, '_sat', name)).convert('RGB')
    W, H = im.size
    k = E / W
    px = im.load()
    dark = []
    gold = []
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            if r < 60 and g < 60 and b < 70 and abs(r - g) < 30:
                dark.append((x, y))
            elif r > 190 and g > 140 and b < 160 and r - b > 70:
                gold.append((x, y))
    # плашка чипа — тёмные пиксели в полосе y 780..980 (2400)
    y0, y1 = int(780 / k), int(980 / k)
    band = [(x, y) for x, y in dark if y0 <= y <= y1]
    if band:
        xs = [x for x, _ in band]
        ys = [y for _, y in band]
        print('тёмная полоса в y780..980: x %.0f..%.0f  y %.0f..%.0f (в 2400)'
              % (min(xs) * k, max(xs) * k, min(ys) * k, max(ys) * k))
    gb = [(x, y) for x, y in gold if y0 <= y <= y1]
    if gb:
        xs = [x for x, _ in gb]
        ys = [y for _, y in gb]
        print('золотой текст:             x %.0f..%.0f  y %.0f..%.0f (в 2400)'
              % (min(xs) * k, max(xs) * k, min(ys) * k, max(ys) * k))
        print('центр текста x=%.0f  (задано 960)' % ((min(xs) + max(xs)) / 2 * k))
    print('задано: плашка 560..1360, текст центр 960, кегль 46')
