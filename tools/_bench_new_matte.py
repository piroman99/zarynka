# -*- coding: utf-8 -*-
"""Матирование новой скамейки + профиль (какая сторона ближняя). Сохраняет matte-файл."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'assets', 'gen', 'prop_bench_new_0.png')
OUT = os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png')


def matte(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(axis=2)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1.0)
    white = (lum > 240) & (sat < 0.08)
    alpha = np.where(white, 0.0, 255.0)
    soft = (~white) & (lum > 215)
    alpha[soft] = np.clip((240.0 - lum[soft]) / 25.0 * 255.0, 0, 255)
    m = alpha > 40
    pad = np.pad(m, 1)
    neigh = sum(pad[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]]
                for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - m
    alpha[m & (neigh < 2)] = 0
    img = Image.fromarray(np.dstack([a, alpha]).astype(np.uint8), 'RGBA')
    bb = img.getchannel('A').point(lambda v: 255 if v > 60 else 0).getbbox()
    return img.crop(bb)


img = matte(SRC)
img.save(OUT)
a = np.asarray(img)
m = a[:, :, 3] > 140
Hf, Wf = m.shape
print('matte %dx%d -> %s %d B' % (Wf, Hf, os.path.relpath(OUT, HERE), os.path.getsize(OUT)))
print('\nпрофиль: где высокая часть (ближний торец), где низкая (дальний)')
print(' x%%   x   верх  низ  высота')
for frac in np.arange(0.02, 1.0, 0.05):
    x = int(frac * Wf)
    col = np.nonzero(m[:, x])[0]
    if col.size == 0:
        print(' %3.0f %4d    -    -       -' % (frac * 100, x))
    else:
        print(' %3.0f %4d  %4d %4d  %5d' % (frac * 100, x, col.min(), col.max(), col.max() - col.min()))
