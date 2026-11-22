# -*- coding: utf-8 -*-
"""Матирование v4 (зелёная крашеная) + замер: ножки, плотность, цвет.

Печатает: фон ли белый, где низ каждой ножки, плотность по полосам, средний цвет
покраски — чтобы «зелёная и новая» было числом, а не на слово.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'assets', 'gen', 'prop_bench_v4_0.png')
OUT = os.path.join(ROOT, '_sat', 'prop_bench_v4_matte.png')


def matte(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(axis=2)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1.0)
    white = (lum > 238) & (sat < 0.10)
    alpha = np.where(white, 0.0, 255.0)
    soft = (~white) & (lum > 210)
    alpha[soft] = np.clip((238.0 - lum[soft]) / 28.0 * 255.0, 0, 255)
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
print('заполнение маски: %.1f%%' % (100.0 * m.mean()))

print('\nплотность по полосам:')
for i in range(8):
    x0, x1 = int(Wf * i / 8), int(Wf * (i + 1) / 8)
    s = a[:, x0:x1, 3]
    print('  x %.2f-%.2f: плотных %5.1f%%  ср.альфа %6.1f' % (i / 8, (i + 1) / 8,
                                                              100 * (s > 200).mean(), s.mean()))

print('\nниз маски по колонкам (шаг 4%), ищем «висящие» участки:')
prev = None
for frac in np.arange(0.02, 1.0, 0.04):
    x = int(frac * Wf)
    col = np.nonzero(m[:, x])[0]
    if not col.size:
        print('  x=%.2f  пусто' % frac)
        continue
    mark = ''
    if prev is not None and abs(col.max() - prev) > 40:
        mark = '  <-- скачок %+d' % (col.max() - prev)
    prev = int(col.max())
    print('  x=%.2f (%4d) низ %4d%s' % (frac, x, col.max(), mark))

print('\nцвет покраски (средний по непрозрачным пикселям, только насыщенные):')
sel = m & ((a[:, :, 2].astype(int) - a[:, :, 1]) < 40)
px = a[sel][:, :3].astype(np.float32)
print('  всего непрозрачных %d, из них «не синих» %d' % (m.sum(), sel.sum()))
print('  средний R%.0f G%.0f B%.0f' % tuple(px.mean(axis=0)))
# отдельно самые зелёные пиксели
g = a[:, :, 1].astype(int) - (a[:, :, 0].astype(int) + a[:, :, 2].astype(int)) // 2
green = m & (g > 12)
print('  зелёных пикселей (G-RB/2 > 12): %d (%.1f%% маски)'
      % (green.sum(), 100.0 * green.sum() / m.sum()))
if green.sum():
    print('  их средний цвет R%.0f G%.0f B%.0f' % tuple(a[green][:, :3].mean(axis=0)))
