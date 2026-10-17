# -*- coding: utf-8 -*-
"""Профиль яркости по строкам в окне, где ожидается плашка (для «до» и «после»)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')

for tag in ('before', 'wide', 'zoom'):
    p = os.path.join(REV, 'review_113_s4_cap_%s.png' % tag)
    im = Image.open(p).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    seg = lum[:, 600:1100]           # центр кадра, где плашка (x) при обоих масштабах
    mean = seg.mean(1)
    mx = seg.max(1)
    print('==', tag, '== (y: mean / max по x 600..1100)')
    prev = None
    for y in range(380, 700, 8):
        bar = '#' * int(mean[y] / 6)
        flag = ''
        if mx[y] > 200 and mean[y] < 40:
            flag = '  <- текст на скриме'
        print('%4d %6.1f %6.1f %s%s' % (y, mean[y], mx[y], bar, flag))
