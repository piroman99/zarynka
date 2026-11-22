# -*- coding: utf-8 -*-
"""Матирование v3-скамейки + профиль низа: доходят ли все ножки до земли."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'assets', 'gen', 'prop_bench_v3_0.png')
OUT = os.path.join(ROOT, '_sat', 'prop_bench_v3_matte.png')


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
m = np.asarray(img)[:, :, 3] > 140
Hf, Wf = m.shape
print('matte %dx%d' % (Wf, Hf))
print('плотность по полосам:')
for i in range(8):
    x0, x1 = int(Wf * i / 8), int(Wf * (i + 1) / 8)
    s = np.asarray(img)[:, x0:x1, 3]
    print('  x %.2f-%.2f: плотных %5.1f%%  ср.альфа %6.1f'
          % (i / 8, (i + 1) / 8, 100 * (s > 200).mean(), s.mean()))

print('\nпрофиль низа (шаг 2%):')
for frac in np.arange(0.02, 1.0, 0.02):
    x = int(frac * Wf)
    col = np.nonzero(m[:, x])[0]
    print('  x=%.2f (%4d) низ %4d' % (frac, x, col.max() if col.size else -1))
