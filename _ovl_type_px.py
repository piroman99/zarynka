# -*- coding: utf-8 -*-
"""Сколько «чернильных» пикселей внутри плашки при разном числе показанных букв.

Плашка полупрозрачная (0.59 тёмного), поэтому даже белый кадр за ней даёт сумму каналов
< ~340; всё, что ярче 600 внутри плашки, — буквы надписи.
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index
S = 1280 / 2400.0


def ink(nid, p, box, extra, thr=600):
    q = ('instant=1&auto=0&text=1&voice=0&music=0&node=%d&page=%d&%s'
         % (node_index(nid), p, extra))
    out = os.path.join(HERE, '.tmp_vo', 'ink_%s_%s.png' % (nid, extra.replace('&', '_')))
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=6000', '--screenshot=' + out,
                    'file://' + IDX + '?' + q], capture_output=True, text=True)
    a = np.asarray(Image.open(out).convert('RGB')).astype(np.int16)
    x0, y0, x1, y1 = [int(v * S) for v in box]
    lum = a[y0:y1, x0:x1].sum(axis=2)
    return int((lum > thr).sum()), out


print('s3 — зона плашки 620..1780 x 330..1010')
for n in (0, 5, 13, 26, 47):
    px, _ = ink('s3', 0, (620, 330, 1780, 1010), 'ovln=%d' % n)
    print('  %2d букв: %5d чернильных px' % (n, px))
print('s5b — чип 801..1599 x 690..780 (золото #ffd278: порог 450)')
for n in (0, 9, 20):
    px, _ = ink('s5b', 0, (801, 690, 1599, 780), 'ovln=%d' % n, 450)
    print('  %2d букв: %5d чернильных px' % (n, px))
