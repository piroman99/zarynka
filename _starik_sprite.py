# -*- coding: utf-8 -*-
"""Старик: вырезать спрайт из assets/gen/starik_0.jpg (серый фон) -> assets/sprites/.
Деспилл: полупрозрачной кромке подставляем цвет БЛИЖАЙШЕГО плотного пикселя
(распространение цвета наружу, numpy) — убирает светлую серую кайму от фона.
"""
import os
import numpy as np
import cutout as C
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', 'gen', 'starik_0.jpg')
DST = os.path.join(HERE, 'assets', 'sprites', 'starik_stern.png')
RAW = os.path.join(HERE, 'assets', 'sprites', '_raw_starik_stern.png')


def despill(im, solid=248, grow=3):
    a = np.asarray(im.convert('RGBA'), np.float32)
    rgb = a[..., :3].copy()
    al = a[..., 3]
    mask = al >= solid                      # плотные пиксели
    cur = rgb.copy()
    known = mask.copy()
    for _ in range(grow):
        acc = np.zeros_like(cur)
        cnt = np.zeros(known.shape, np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            k = np.roll(np.roll(known, dy, 0), dx, 1)
            v = np.roll(np.roll(cur, dy, 0), dx, 1)
            acc += v * k[..., None]
            cnt += k
        fill = (~known) & (cnt > 0)
        cur[fill] = acc[fill] / cnt[fill][:, None]
        known |= fill
    out = rgb.copy()
    soft = al < solid
    out[soft] = cur[soft]
    res = np.dstack([out, al]).astype(np.uint8)
    return Image.fromarray(res, 'RGBA')


def edge_profile(im, tag):
    px = im.load()
    w, h = im.size
    L = []
    for y in range(int(h * 0.60), int(h * 0.99), max(1, h // 40)):
        xs = [x for x in range(w) if px[x, y][3] > 10]
        if not xs:
            continue
        for x in xs[:2] + xs[-2:]:
            r, g, b, a = px[x, y]
            L.append((0.299 * r + 0.587 * g + 0.114 * b, a))
    n = len(L)
    light = sum(1 for v, _ in L if v > 170)
    print('   %-6s кромка: n=%d светлых(L>170) %.1f%% средняя L %.0f'
          % (tag, n, 100.0 * light / n, sum(v for v, _ in L) / n))


raw = C.cutout(SRC, RAW, tol=34)
im = Image.open(raw).convert('RGBA')
edge_profile(im, 'до')
im2 = despill(im)
im2.save(DST, 'PNG')
edge_profile(im2, 'после')
print('->', os.path.relpath(DST, HERE), im2.size, os.path.getsize(DST), 'B')
