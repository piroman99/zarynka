# -*- coding: utf-8 -*-
"""Разведка фона аллеи без зрения: где горизонтальные линии (доски скамейки) и
вертикальные (ножки, столб фонаря). Печатаем ASCII карты градиентов по областям."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'vn2', 'img', 'bg', 'alley.webp')

REGIONS = [
    ('left-bottom', 0.00, 0.55, 0.30, 1.00),
    ('mid-bottom', 0.25, 0.75, 0.30, 1.00),
]


def ascii_map(a, cols, rows, label):
    H, W = a.shape
    print('\n--- %s (%d x %d) ---' % (label, W, H))
    vmax = np.percentile(a, 99) + 1e-6
    chars = ' .:-=+*#%@'
    for r in range(rows):
        y0, y1 = int(r * H / rows), int((r + 1) * H / rows)
        line = []
        for c in range(cols):
            x0, x1 = int(c * W / cols), int((c + 1) * W / cols)
            v = a[y0:y1, x0:x1].mean() / vmax
            line.append(chars[min(9, int(v * 9.99))])
        print('|' + ''.join(line) + '|')


im = Image.open(P).convert('RGB')
W0, H0 = im.size
a = np.asarray(im).astype(np.float32)
lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
gy = np.zeros_like(lum)
gx = np.zeros_like(lum)
gy[1:-1, :] = np.abs(lum[2:, :] - lum[:-2, :]) * 0.5
gx[:, 1:-1] = np.abs(lum[:, 2:] - lum[:, :-2]) * 0.5

for name, x0f, x1f, y0f, y1f in REGIONS:
    x0, x1 = int(x0f * W0), int(x1f * W0)
    y0, y1 = int(y0f * H0), int(y1f * H0)
    sub_y = gy[y0:y1, x0:x1]
    sub_x = gx[y0:y1, x0:x1]
    print('\n===== %s  x %d..%d y %d..%d =====' % (name, x0, x1, y0, y1))
    ascii_map(sub_y, 100, 34, 'ГОРИЗОНТАЛЬНЫЕ линии (|dY|)')
    ascii_map(sub_x, 100, 34, 'ВЕРТИКАЛЬНЫЕ линии (|dX|)')
