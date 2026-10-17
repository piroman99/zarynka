# -*- coding: utf-8 -*-
"""Точная геометрия экрана ТВ в плашке S4."""
import os
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets/final/prolog/s4.png')).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)

blur = np.asarray(Image.fromarray(lum.astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
hp = np.abs(lum - blur)

crop = hp[100:800, 400:1600]
rows = crop.mean(1)
cols = crop.mean(0)
print('rows peaks:', [(int(i) + 100, round(float(rows[i]), 2)) for i in np.argsort(rows)[-8:]])
print('cols peaks:', [(int(i) + 400, round(float(cols[i]), 2)) for i in np.argsort(cols)[-8:]])

chars = ' .:-=+*#%@'
CW, CH = 96, 40
x0, y0, x1, y1 = 400, 60, 1600, 780
c = im.crop((x0, y0, x1, y1)).resize((CW, CH), Image.BILINEAR)
p = c.load()
hdr = '     ' + ''.join(str((x0 + int(xx * (x1 - x0) / CW)) // 100 % 10) for xx in range(CW))
print(hdr)
for yy in range(CH):
    row = ''
    for xx in range(CW):
        r, g, b = p[xx, yy]
        v = (r * 0.299 + g * 0.587 + b * 0.114) / 255
        row += chars[min(9, int(v * 10))]
    print('%4d|%s' % (y0 + int(yy * (y1 - y0) / CH), row))
