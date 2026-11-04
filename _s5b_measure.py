# -*- coding: utf-8 -*-
"""Точный замер чипа кадра 12 в живом демо: bbox тёмной плашки и bbox золотого текста
в пространстве 2400x1350. Сравниваем с заданным (560..1360 / текст центр 960)."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
E = 2400.0
im = Image.open(os.path.join(HERE, '_sat', 'demo_s5b.png')).convert('RGB')
W, H = im.size
k = E / W
px = im.load()

y0, y1 = int(820 / k), int(935 / k)          # полоса чипа с запасом


def near(p, c, tol):
    return all(abs(p[i] - c[i]) <= tol for i in range(3))


dark, gold = [], []
for y in range(y0, y1):
    for x in range(W):
        p = px[x, y]
        if near(p, (6, 8, 14), 22):
            dark.append((x, y))
        if near(p, (255, 210, 120), 70) or (p[0] > 200 and 150 < p[1] < 235 and p[2] < 170):
            gold.append((x, y))

for name, pts in (('плашка', dark), ('текст', gold)):
    if not pts:
        print(name, 'не найдено')
        continue
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    print('%-7s x %4.0f..%4.0f (центр %4.0f, ширина %3.0f)  y %4.0f..%4.0f'
          % (name, min(xs) * k, max(xs) * k, (min(xs) + max(xs)) / 2 * k,
             (max(xs) - min(xs)) * k, min(ys) * k, max(ys) * k))
print('задано  плашка x  560..1360 (центр  960)  y  830..920')
print('кадр 2400x1350 → центр кадра x=1200')
