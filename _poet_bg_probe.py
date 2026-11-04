# -*- coding: utf-8 -*-
"""Диагностика фона спрайта: углы, стороны, ASCII-карта (готов ли к cutout())."""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')

for name in (sys.argv[1:] or ['poet_a_0.png', 'poet_b_0.png']):
    p = os.path.join(GEN, name)
    a = np.asarray(Image.open(p).convert('RGB'), np.int16)
    h, w, _ = a.shape
    print('\n%s %dx%d' % (name, w, h))
    for lbl, side in (('top', a[0]), ('bot', a[-1]), ('left', a[:, 0]), ('right', a[:, -1])):
        print('  %-5s mean %s  min %d  max %d' % (lbl, side.mean(0).round().tolist(),
                                                  side.min(), side.max()))
    print('  углы TL %s TR %s BL %s BR %s' % (a[0, 0].tolist(), a[0, -1].tolist(),
                                              a[-1, 0].tolist(), a[-1, -1].tolist()))
    COLS, ROWS = 20, 14
    for ry in range(ROWS):
        line = ''
        for rx in range(COLS):
            blk = a[ry * h // ROWS:(ry + 1) * h // ROWS, rx * w // COLS:(rx + 1) * w // COLS]
            m = blk.mean(2).mean()
            line += ' ' if m > 225 else ('.' if m > 190 else ('o' if m > 150 else
                                                             ('#' if m > 90 else '@')))
        print('   ' + line)
