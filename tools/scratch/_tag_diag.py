# -*- coding: utf-8 -*-
"""Диагностика: что реально в верхнем левом углу финального кадра s5a."""
from PIL import Image

im = Image.open('assets/final/prolog/s5a.png').convert('RGB')
W, H = im.size
print('size', W, H)
px = im.load()
for y in range(40, 120, 8):
    vals = [px[x, y] for x in range(40, 400, 40)]
    print(y, vals)
print('--- тёмные пиксели по строкам ---')
for y in range(40, 120, 4):
    xs = [x for x in range(0, 900) if sum(px[x, y]) < 90]
    print(y, 'n=%d' % len(xs), (min(xs), max(xs)) if xs else '')
