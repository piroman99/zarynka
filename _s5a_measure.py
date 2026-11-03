# -*- coding: utf-8 -*-
"""Замер светлого стенда на кадре 11 (s5a) — куда ляжет полоса лозунга."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
for name in ('s5a_a__gpt-image-2_0.png', 's5a_b__gpt-image-2_0.png'):
    im = Image.open(os.path.join(GEN, name)).convert('RGB')
    w, h = im.size
    a = np.asarray(im, np.float32)
    # «светлая бумага»: ярко и низкая насыщенность
    mx = a.max(2); mn = a.min(2)
    mask = (mx > 150) & ((mx - mn) < 26)
    # ищем крупнейший светлый прямоугольник: считаем по строкам/столбцам долю маски
    rows = mask.mean(1); cols = mask.mean(0)
    def span(v, thr):
        idx = np.where(v > thr)[0]
        return (int(idx[0]), int(idx[-1])) if len(idx) else None
    print('==', name, im.size)
    print('  rows>0.25:', span(rows, 0.25), ' rows>0.4:', span(rows, 0.4))
    print('  cols>0.15:', span(cols, 0.15), ' cols>0.3:', span(cols, 0.3))
    # в правой трети (стенд-витрина в варианте A)
    right = mask[:, int(w * 0.55):]
    r_rows = right.mean(1); r_cols = right.mean(0)
    print('  right rows>0.5:', span(r_rows, 0.5), 'right cols>0.4:', span(r_cols, 0.4))
    # точные границы самого большого светлого блоба (грубо: bbox маски в правой половине)
    ys, xs = np.where(right)
    if len(xs):
        print('  right bbox: x %d..%d  y %d..%d (offset x+%d)'
              % (xs.min() + int(w * 0.55), xs.max() + int(w * 0.55), ys.min(), ys.max(), int(w * 0.55)))
