# -*- coding: utf-8 -*-
"""Точное измерение цвета CREAM (246,238,222) в кадрах «до/после» наезда."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')


def scan(tag):
    p = os.path.join(REV, 'review_113_s4_cap_%s.png' % tag)
    im = Image.open(p).convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (np.abs(r - 246) < 12) & (np.abs(g - 238) < 12) & (np.abs(b - 222) < 14)
    ys, xs = np.nonzero(m)
    if len(xs) < 50:
        return tag, None
    # группируем по строкам: ищем плотную полосу
    rows = m.sum(1)
    band = [y for y in range(H) if rows[y] > 40]
    blocks, cur = [], []
    for y in band:
        if cur and y != cur[-1] + 1:
            blocks.append(cur); cur = []
        cur.append(y)
    if cur:
        blocks.append(cur)
    res = []
    for bl in blocks:
        sel = m[bl[0]:bl[-1] + 1]
        bx = np.nonzero(sel.sum(0))[0]
        res.append((bl[0], bl[-1], int(bx.min()), int(bx.max()), len(bl)))
    return tag, res


for tag in ('before', 'wide', 'zoom'):
    t, res = scan(tag)
    print('==', t, '==')
    if not res:
        print('   кремовых полос нет')
        continue
    for y0, y1, x0, x1, n in res:
        print('   полоса y %d..%d (h=%d, строк %d)  x %d..%d' % (y0, y1, y1 - y0 + 1, n, x0, x1))
    print('   #box верх = 641 (1600x900)')
