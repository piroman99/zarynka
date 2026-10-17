# -*- coding: utf-8 -*-
"""Замер v2: ищем плашку в ОЖИДАЕМОМ окне (не по всему кадру)."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(HERE, 'assets', 'review')

# ожидание из геометрии сборки: плашка 0.507..0.564 по y (-> масштаб наезда)
EXP = {'wide': (0.30, 0.70, 0.44, 0.64), 'zoom': (0.26, 0.78, 0.58, 0.72)}
BOX = {}


def dark_band_small(im, win):
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    x0, x1 = int(win[0] * W), int(win[1] * W)
    y0, y1 = int(win[2] * H), int(win[3] * H)
    sub = lum[y0:y1, x0:x1]
    scr = sub < 45
    ys, xs = np.nonzero(scr)
    if len(xs) < 200:
        return None
    # строка считается "в плашке", если тёмных > 30% ширины окна
    rows = scr.sum(1)
    good = [i for i in range(scr.shape[0]) if rows[i] > 0.25 * scr.shape[1]]
    return (x0 + xs.min(), x0 + xs.max(), y0 + good[0], y0 + good[-1]) if good else None


for tag in ('wide', 'zoom'):
    p = os.path.join(REV, 'review_113_s4_cap_%s.png' % tag)
    im = Image.open(p).convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 170) & (g < 110) & (b < 110)
    rows = red.sum(1)
    box_top = min([y for y in range(H) if rows[y] > W * 0.5] or [None])
    # скрим ищем в окне всего кадра, но НИЖЕ телевизора
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    scr = lum < 45
    rows_s = scr.sum(1)
    band = [y for y in range(H) if rows_s[y] > W * 0.25 and (box_top is None or y < box_top - 3)]
    # берём непрерывный блок сразу над самым низом
    blocks, cur = [], []
    for y in band:
        if cur and y != cur[-1] + 1:
            blocks.append(cur); cur = []
        cur.append(y)
    if cur:
        blocks.append(cur)
    blocks = [bl for bl in blocks if len(bl) > 15]
    bt, bb = (blocks[-1][0], blocks[-1][-1]) if blocks else (None, None)
    print('%s: #box верх=%d (%.1f%%), плашка-скрим y %s..%s' % (tag, box_top, 100.0 * box_top / H, bt, bb))
    if bt:
        cols = scr[bt:bb + 1].sum(0)
        xs = [x for x in range(W) if cols[x] > 0]
        print('   по x: %d..%d (ширина %d px)' % (min(xs), max(xs), max(xs) - min(xs)))
        # текст внутри плашки: светлые пиксели
        sub = lum[bt:bb + 1, min(xs):max(xs) + 1]
        t_ys, t_xs = np.nonzero(sub > 150)
        if len(t_ys):
            print('   текст: высота %d px, ширина %d px, зазор до #box %d px'
                  % (t_ys.max() - t_ys.min() + 1, t_xs.max() - t_xs.min() + 1,
                     box_top - (bb)))
