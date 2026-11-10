# -*- coding: utf-8 -*-
"""Крупный ASCII по яркости вокруг подозреваемого пятна в фоне аллеи (x 440..620, y 580..730).

Нужен, чтобы понять, есть ли там нарисованная скамейка и какая у неё форма:
печатаем яркость (10 оттенков) и отдельно маску «темнее среднего».
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'vn2', 'img', 'bg', 'alley.webp')).convert('RGB')
a = np.asarray(im).astype(np.float32)
lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

X0, X1, Y0, Y1 = 430, 630, 570, 740
sub = lum[Y0:Y1, X0:X1]
lo, hi = np.percentile(sub, 3), np.percentile(sub, 97)
print('окно x %d..%d y %d..%d, яркость %.0f..%.0f (3..97 пц), среднее %.0f'
      % (X0, X1, Y0, Y1, lo, hi, sub.mean()))
chars = ' .:-=+*#%@'
cols, rows = 80, 34
print('\n--- яркость ---')
for r in range(rows):
    line = []
    for c in range(cols):
        ya, yb = int(r * sub.shape[0] / rows), int((r + 1) * sub.shape[0] / rows)
        xa, xb = int(c * sub.shape[1] / cols), int((c + 1) * sub.shape[1] / cols)
        v = (sub[ya:yb, xa:xb].mean() - lo) / max(1e-6, hi - lo)
        line.append(chars[max(0, min(9, int(v * 9.99)))])
    print('|' + ''.join(line) + '|  y=%d' % (Y0 + int(r * sub.shape[0] / rows)))

print('\n--- темнее среднего на 12 ---')
dark = sub < sub.mean() - 12
for r in range(rows):
    line = []
    for c in range(cols):
        ya, yb = int(r * dark.shape[0] / rows), int((r + 1) * dark.shape[0] / rows)
        xa, xb = int(c * dark.shape[1] / cols), int((c + 1) * dark.shape[1] / cols)
        f = dark[ya:yb, xa:xb].mean()
        line.append('#' if f > 0.5 else ('+' if f > 0.2 else ('.' if f > 0.05 else ' ')))
    print('|' + ''.join(line) + '|  y=%d' % (Y0 + int(r * dark.shape[0] / rows)))
