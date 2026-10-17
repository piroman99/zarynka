# -*- coding: utf-8 -*-
"""Полная ASCII-карта скриншота + цвета в ключевых точках."""
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
tag = sys.argv[1] if len(sys.argv) > 1 else 'zoom'
im = Image.open(os.path.join(REV, 'review_113_s4_cap_%s.png' % tag)).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
CW, CH = 100, 45
c = im.resize((CW, CH), Image.BILINEAR)
b = np.asarray(c).astype(np.float32)
cl = b @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
chars = ' .:-=+*#%@'
print('    ' + ''.join(str(int(i * W / CW) // 100 % 10) for i in range(CW)))
for y in range(CH):
    print('%4d|%s' % (int(y * H / CH), ''.join(chars[min(9, int(cl[y, x] / 25.6))] for x in range(CW))))
print()
for y, x in ((600, 800), (650, 800), (700, 800), (800, 800), (860, 800), (650, 120), (890, 800)):
    print('pixel y=%d x=%d ->' % (y, x), im.getpixel((x, y)))
