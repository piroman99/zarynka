# -*- coding: utf-8 -*-
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets/final/prolog/s4.png')).convert('RGB')
print('s4.png', im.size)
W, H = im.size
sm = im.resize((60, 34), Image.BILINEAR)
px = sm.load()
chars = ' .:-=+*#%@'
for y in range(34):
    row = ''
    for x in range(60):
        r, g, b = px[x, y]
        v = (r * 0.299 + g * 0.587 + b * 0.114) / 255
        row += chars[min(9, int(v * 10))]
    print('%2d|%s' % (y, row))

small = im.resize((W // 8, H // 8))
sp = small.load()
sw, sh = small.size
warm = []
blue = []
for y in range(sh):
    for x in range(sw):
        r, g, b = sp[x, y]
        if b > 60 and b > r + 25:
            blue.append((x, y))
        if r > 120 and r > b + 40 and g > 80:
            warm.append((x, y))
for nm, pts in (('blue bbox x8', blue), ('warm bbox x8', warm)):
    if pts:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        print(nm, min(xs) * 8, min(ys) * 8, max(xs) * 8, max(ys) * 8, 'n=', len(pts))
