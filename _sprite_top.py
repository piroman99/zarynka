# -*- coding: utf-8 -*-
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
d = os.path.join(HERE, 'vn2', 'img', 'char')
for f in sorted(os.listdir(d)):
    im = Image.open(os.path.join(d, f)).convert('RGBA')
    w, h = im.size
    a = im.split()[3]
    bbox = a.getbbox()
    # сколько строк сверху прозрачны
    px = a.load()
    top = 0
    for y in range(h):
        row = [px[x, y] for x in range(0, w, 3)]
        if max(row) > 8:
            break
        top = y + 1
    cut_px = int(0.04 * h)
    print('%-24s %dx%d bbox=%s  прозрачно сверху=%dpx  срезается 4%%=%dpx -> %s'
          % (f, w, h, bbox, top, cut_px, 'ГОЛОВА РЕЖЕТСЯ' if top < cut_px else 'ок'))
