# -*- coding: utf-8 -*-
"""Насколько десктопный титул изменился от правок (ожидаем: только кнопка ⛶)."""
import os
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, '.tmp_mob')
for what in ('title', 's1'):
    a = Image.open(os.path.join(T, 'before_desk_%s.png' % what)).convert('RGB')
    b = Image.open(os.path.join(T, 'after_desk_%s.png' % what)).convert('RGB')
    if a.size != b.size:
        print(what, 'РАЗНЫЙ РАЗМЕР', a.size, b.size)
        continue
    df = ImageChops.difference(a, b).convert('L')
    px = list(df.getdata())
    n = len(px)
    changed = sum(1 for v in px if v > 12) / n
    box = df.point(lambda v: 255 if v > 12 else 0).getbbox()
    print('desktop %-5s изменённых пикселей %.4f%%  рамка %s' % (what, changed * 100, box))
