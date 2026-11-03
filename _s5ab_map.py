# -*- coding: utf-8 -*-
"""ASCII-карта яркости/красноты кадра 11 (вариант B): понять, куда ложится полоса лозунга."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'assets', 'gen', 's5a_b__gpt-image-2_0.png')
im = Image.open(p).convert('RGB')
W, H = im.size
print('size', W, H)
g = im.resize((60, 34), Image.LANCZOS)
px = g.load()
ramp = ' .:-=+*#%@'
for y in range(34):
    row = ''
    for x in range(60):
        r, gg, b = px[x, y]
        lum = (0.299 * r + 0.587 * gg + 0.114 * b)
        row += ramp[min(9, int(lum / 25.6))]
    print('%2d|%s' % (y, row))
print()
for y in range(34):
    row = ''
    for x in range(60):
        r, gg, b = px[x, y]
        v = max(0, r - max(gg, b))
        row += '#' if v > 40 else ('+' if v > 20 else '.')
    print('%2d|%s' % (y, row))
