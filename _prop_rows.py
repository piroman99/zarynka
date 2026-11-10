# -*- coding: utf-8 -*-
"""Яркость по строкам внутри маски пропа (ближняя треть): где светлые «крыши» досок
и тёмные полосы под ними. По этому видно спинку (рейки) и сиденье.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets', 'sprites', 'prop_bench.png')).convert('RGBA')
rgb = np.asarray(im.convert('RGB')).astype(np.float32)
a = np.asarray(im.split()[-1])
m = a > 140
lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
h, w = lum.shape
ys, xs = np.nonzero(m)
x0, x1 = xs.min(), xs.max()

for label, xa, xb in (('ближняя треть 5..30%', 0.05, 0.30), ('середина 40..55%', 0.40, 0.55)):
    sub_m = m[:, int(x0 + xa * (x1 - x0)):int(x0 + xb * (x1 - x0))]
    sub_l = lum[:, int(x0 + xa * (x1 - x0)):int(x0 + xb * (x1 - x0))]
    rows = np.nonzero(sub_m.any(1))[0]
    y0, y1 = rows.min(), rows.max()
    print('\n=== %s: y %d..%d ===' % (label, y0, y1))
    print('  y     %покр  яркость')
    for y in range(y0, y1 + 1, 8):
        cov = sub_m[y].mean()
        val = sub_l[y][sub_m[y]].mean() if sub_m[y].any() else float('nan')
        bar = '#' * int(max(0.0, min(1.0, (val - 60) / 140.0)) * 40)
        print('  %4d  %4.0f%%  %5.0f  %s' % (y, 100 * cov, val, bar))
