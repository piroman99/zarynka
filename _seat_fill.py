# -*- coding: utf-8 -*-
"""Замер сидящих спрайтов поэта: насколько РАЗНЫЙ масштаб фигуры у 6 эмоций.

Считаем по альфе: bbox фигуры, высота фигуры / высота холста (FIG_FILL), ширина головы
(верхние 12 % bbox), и где должна быть линия бёдер (0.346 высоты фигуры от низа —
для сидящего человека посадка 0.45 м при росте сидя 1.30 м).
"""
import os
import glob

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(HERE, 'assets', 'sprites')

print('%-26s %11s %11s %8s %8s %9s %9s' % ('файл', 'холст', 'фигура', 'fill',
                                           'голова', 'бедро%', 'голова/h'))
for p in sorted(glob.glob(os.path.join(SPR, 'poet_seat_*.png'))):
    im = Image.open(p)
    a = np.asarray(im.convert('RGBA').split()[-1])
    m = a > 128
    ys, xs = np.nonzero(m)
    if not len(ys):
        print('%-26s пусто' % os.path.basename(p))
        continue
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0 + 1
    band = m[y0:y0 + max(2, int(bh * 0.12))]
    cols = np.nonzero(band.any(0))[0]
    hd = int(cols.max() - cols.min()) if len(cols) else 0
    fill = bh / im.height
    hip = 0.346 * bh                    # px от низа фигуры
    hip_from_bottom_canvas = (im.height - 1 - y1) + hip
    print('%-26s %5dx%-5d %5dx%-5d %7.3f %8d %8.1f%% %9.3f'
          % (os.path.basename(p), im.width, im.height, xs.max() - xs.min() + 1, bh,
             fill, hd, 100.0 * hip_from_bottom_canvas / im.height, hd / im.height))
