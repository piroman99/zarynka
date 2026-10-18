# -*- coding: utf-8 -*-
"""ASCII-профиль кромки: L первых/последних 7 px силуэта в нижней трети."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets', 'sprites', 'starik_stern.png')).convert('RGBA')
px = im.load()
w, h = im.size
print('sprite', w, h)
for y in range(int(h * 0.60), int(h * 0.99), max(1, (h // 40))):
    xs = [x for x in range(w) if px[x, y][3] > 10]
    if not xs:
        continue
    left = ['%3d/%3d' % (int(0.299 * px[x, y][0] + 0.587 * px[x, y][1] + 0.114 * px[x, y][2]), px[x, y][3])
            for x in xs[:6]]
    right = ['%3d/%3d' % (int(0.299 * px[x, y][0] + 0.587 * px[x, y][1] + 0.114 * px[x, y][2]), px[x, y][3])
             for x in xs[-6:]]
    print('y=%4d  L %s   |   %s' % (y, ' '.join(left), ' '.join(right)))
