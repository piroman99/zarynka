# -*- coding: utf-8 -*-
"""Точный замер слоя на кадре 12: диф on/off в полосе чипа, bbox в 2400-пространстве
(правильный пересчёт) + оценка масштаба/смещения слоя."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
E = 2400.0
A = Image.open(os.path.join(HERE, '_sat', 's5b_on.png')).convert('RGB')
B = Image.open(os.path.join(HERE, '_sat', 's5b_off.png')).convert('RGB')
W, H = A.size
S = E / W                      # пиксель -> 2400-пространство
pa, pb = A.load(), B.load()

pts = []
for y in range(int(700 / S), int(1000 / S)):
    for x in range(int(200 / S), int(1800 / S)):
        ra, ga, ba = pa[x, y]
        rb, gb, bb = pb[x, y]
        if abs(ra - rb) + abs(ga - gb) + abs(ba - bb) > 40:
            pts.append((x, y))
if not pts:
    raise SystemExit('нет различий')
xs = [x for x, _ in pts]
ys = [y for _, y in pts]
got = (min(xs) * S, min(ys) * S, max(xs) * S, max(ys) * S)
print('слой по факту: x %.0f..%.0f  y %.0f..%.0f' % got)
print('задано:        x 560..1360  y 830..920')
w_got, w_exp = got[2] - got[0], 800.0
h_got, h_exp = got[3] - got[1], 90.0
print('масштаб по ширине %.3f, по высоте %.3f' % (w_got / w_exp, h_got / h_exp))
print('смещение левого верхнего: dx=%.0f dy=%.0f' % (got[0] - 560, got[1] - 830))
