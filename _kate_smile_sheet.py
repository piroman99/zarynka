# -*- coding: utf-8 -*-
"""Катя: база / sad / новая smile — лица крупно + метрики возраста (морщины, кудри)."""
import os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
K2 = os.path.join(GEN, '_kate_v2')
REV = os.path.join(HERE, 'assets', 'review')

FILES = [('база neutral', os.path.join(GEN, 'kate_overalls_0.png')),
         ('sad (в сборке)', os.path.join(GEN, 'kate_sad_0.png')),
         ('smile НОВАЯ', os.path.join(K2, 'kate_smile__gpt-image-2_0.png'))]

TW = 620
tiles = []
for label, p in FILES:
    im = Image.open(p).convert('RGB')
    w, h = im.size
    f = im.crop((int(w * .20), int(h * .03), int(w * .80), int(h * .40)))
    f = f.resize((TW, int(f.height * TW / f.width)), Image.LANCZOS)
    tiles.append((label, f))
th = tiles[0][1].height
sheet = Image.new('RGB', (TW * len(tiles), th + 26), (12, 14, 20))
d = ImageDraw.Draw(sheet)
for i, (label, im) in enumerate(tiles):
    sheet.paste(im, (i * TW, 26))
    d.text((i * TW + 8, 8), label, fill=(255, 255, 255))
p = os.path.join(REV, 'review_79_kate_smile.png')
sheet.save(p)
print(p, sheet.size)

# метрики: морщины лица и «седина» (доля очень светлых пикселей в волосах)
def stats(path):
    a = np.asarray(Image.open(path).convert('RGB'), np.float32)
    h, w, _ = a.shape
    face = a[int(h * .10):int(h * .34), int(w * .28):int(w * .72)]
    g = face.mean(2)
    lap = np.abs(4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]).mean()
    hair = a[int(h * .03):int(h * .16), int(w * .22):int(w * .78)]
    grey = (hair.mean(2) > 150).mean()
    return lap, grey

print('%-16s %8s %8s' % ('', 'морщины', 'седина'))
for label, p in FILES:
    lap, grey = stats(p)
    print('%-16s %8.2f %8.1f%%' % (label, lap, 100 * grey))
