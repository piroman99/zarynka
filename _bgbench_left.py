# -*- coding: utf-8 -*-
"""Левый нижний угол фона аллеи: нарисованная скамейка у края кадра.

Окно x 0..260, y 780..1010 в фоне 1920x1080: яркость + маска «дерева», чтобы понять
форму пятна и что вокруг (трава/асфальт/тень).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'vn2', 'img', 'bg', 'alley.webp')).convert('RGB')
a = np.asarray(im).astype(np.float32)
W, H = im.size
lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
hsv = np.asarray(im.convert('HSV')).astype(np.int16)
Hc, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
wood = (Hc >= 6) & (Hc <= 32) & (S >= 55) & (V >= 45) & (V <= 210)
green = (Hc >= 40) & (Hc <= 110) & (S >= 40)

X0, X1, Y0, Y1 = 0, 260, 780, 1010
sub_l = lum[Y0:Y1, X0:X1]
sub_w = wood[Y0:Y1, X0:X1]
sub_g = green[Y0:Y1, X0:X1]
lo, hi = np.percentile(sub_l, 2), np.percentile(sub_l, 98)
print('окно x %d..%d y %d..%d, яркость %.0f..%.0f, дерево %.1f%%, зелень %.1f%%'
      % (X0, X1, Y0, Y1, lo, hi, 100 * sub_w.mean(), 100 * sub_g.mean()))
chars = ' .:-=+*#%@'
cols, rows = 78, 32


def grid(mask, label):
    print('\n--- %s ---' % label)
    for r in range(rows):
        line = []
        for c in range(cols):
            ya, yb = int(r * mask.shape[0] / rows), int((r + 1) * mask.shape[0] / rows)
            xa, xb = int(c * mask.shape[1] / cols), int((c + 1) * mask.shape[1] / cols)
            f = mask[ya:yb, xa:xb].mean()
            line.append('#' if f > 0.5 else ('+' if f > 0.2 else ('.' if f > 0.05 else ' ')))
        print('|' + ''.join(line) + '|  y=%d' % (Y0 + int(r * mask.shape[0] / rows)))


grid(sub_w, 'дерево')
grid(sub_g, 'зелень')
print('\n--- яркость ---')
for r in range(rows):
    line = []
    for c in range(cols):
        ya, yb = int(r * sub_l.shape[0] / rows), int((r + 1) * sub_l.shape[0] / rows)
        xa, xb = int(c * sub_l.shape[1] / cols), int((c + 1) * sub_l.shape[1] / cols)
        v = (sub_l[ya:yb, xa:xb].mean() - lo) / max(1e-6, hi - lo)
        line.append(chars[max(0, min(9, int(v * 9.99)))])
    print('|' + ''.join(line) + '|  y=%d' % (Y0 + int(r * sub_l.shape[0] / rows)))
