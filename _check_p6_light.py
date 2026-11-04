# -*- coding: utf-8 -*-
"""Яркость кадра p6 (лунная станция) по полосам: не «выпал ли» кадр в темноту.

    python3 _check_p6_light.py

Печатает среднюю яркость и долю тёмных пикселей по горизонтальным полосам для
финального кадра p6 и, для сравнения, для соседних кадров пролога (p7, s3).
"""
import os
import numpy as np
from PIL import Image

FIN = os.path.join('assets', 'final', 'prolog')
BANDS = [('небо', 0.00, 0.35), ('середина', 0.35, 0.65), ('земля', 0.65, 1.00)]

for name in ('p6', 'p7', 'p8', 's3'):
    p = os.path.join(FIN, name + '.png')
    if not os.path.exists(p):
        continue
    a = np.asarray(Image.open(p).convert('L'), np.float32)
    h = a.shape[0]
    out = []
    for lab, y0, y1 in BANDS:
        b = a[int(y0 * h):int(y1 * h)]
        out.append('%s %.0f (тёмных %.0f%%)' % (lab, b.mean(), (b < 40).mean() * 100))
    print('%-4s %s' % (name, ' | '.join(out)))
