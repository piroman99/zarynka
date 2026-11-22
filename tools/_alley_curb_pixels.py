# -*- coding: utf-8 -*-
"""Найти бордюр по пикселям: светлые каменные блоки в левой части кадра.

Модели со зрением дают противоречивые координаты, поэтому ищем сами: бордюр нарисован
светлыми (высокая яркость, низкая насыщенность) блоками, а газон — темнее и зеленее.
Для каждой строки берём самый светлый участок в левой трети, собираем точки, фитим
прямую RANSAC-ом и печатаем x бордюра на нужных высотах.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
W, H = 1920, 1080

im = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
lum = a.mean(axis=2)
mx, mn = a.max(axis=2), a.min(axis=2)
sat = (mx - mn) / np.maximum(mx, 1.0)
bright = (lum > 175) & (sat < 0.16)

print('ярких малонасыщенных пикселей: %d (%.1f%%)' % (bright.sum(), 100.0 * bright.mean()))
print('\nпо строкам: сколько ярких пикселей в левой трети и где они (x мин/макс)')
pts = []
for y in range(int(H * 0.55), H, 6):
    row = bright[y, :int(W * 0.45)]
    idx = np.nonzero(row)[0]
    if idx.size < 6:
        continue
    print('  y=%4d  n=%3d  x %4d..%4d' % (y, idx.size, idx.min(), idx.max()))
    pts.append((idx.min(), y))

if len(pts) > 20:
    pts = np.array(pts, dtype=np.float64)
    rng = np.random.default_rng(3)
    best = None
    for _ in range(800):
        i, j = rng.integers(0, len(pts), 2)
        if abs(pts[i, 1] - pts[j, 1]) < 60:
            continue
        k = (pts[i, 0] - pts[j, 0]) / (pts[i, 1] - pts[j, 1])
        b = pts[i, 0] - k * pts[i, 1]
        res = np.abs(pts[:, 0] - (k * pts[:, 1] + b))
        inl = res < 20
        if best is None or inl.sum() > best[0]:
            best = (int(inl.sum()), k, b, inl)
    n, k, b, inl = best
    A = np.vstack([pts[inl, 1], np.ones(inl.sum())]).T
    k, b = np.linalg.lstsq(A, pts[inl, 0], rcond=None)[0]
    print('\nRANSAC: инлайеров %d/%d, x = %.4f*y %+.1f' % (n, len(pts), k, b))
    for y in (830, 860, 900, 925, 960, 1000, 1040):
        print('  y=%4d -> бордюр x=%.0f' % (y, k * y + b))
