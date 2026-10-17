# -*- coding: utf-8 -*-
"""ASCII-карта участка скриншота, чтобы глазами найти плашку и #box."""
import os
import sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')
tag = sys.argv[1] if len(sys.argv) > 1 else 'zoom'
x0, y0, x1, y1 = [int(v) for v in (sys.argv[2:6] or (480, 380, 1240, 720))]
im = Image.open(os.path.join(REV, 'review_113_s4_cap_%s.png' % tag)).convert('RGB')
CW, CH = 95, 40
c = im.crop((x0, y0, x1, y1)).resize((CW, CH), Image.BILINEAR)
a = np.asarray(c).astype(np.float32)
lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
chars = ' .:-=+*#%@'
print('    ' + ''.join(str((x0 + int(i * (x1 - x0) / CW)) // 100 % 10) for i in range(CW)))
for yy in range(CH):
    row = ''.join(chars[min(9, int(lum[yy, xx] / 25.6))] for xx in range(CW))
    print('%4d|%s' % (y0 + int(yy * (y1 - y0) / CH), row))
