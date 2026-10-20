# -*- coding: utf-8 -*-
"""Что за пределами диска в vn2/img/logo.png: кремовый фон, белый или прозрачность."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for rel in ('vn2/img/logo.png', 'assets/gen/logo_b_0.jpg', 'assets/gen/znachek_k1.png'):
    p = os.path.join(HERE, rel)
    im = Image.open(p)
    print('%-28s %s mode=%s' % (rel, im.size, im.mode))
    a = np.asarray(im.convert('RGB'), dtype=np.int16)
    h, w = a.shape[:2]
    corners = [a[2, 2], a[2, w - 3], a[h - 3, 2], a[h - 3, w - 3]]
    print('   углы RGB:', [tuple(int(x) for x in c) for c in corners])
    print('   центр RGB:', tuple(int(x) for x in a[h // 2, w // 2]))
    if im.mode == 'RGBA':
        al = np.asarray(im)[:, :, 3]
        print('   альфа: мин %d, доля прозрачных %.1f%%'
              % (al.min(), (al < 10).mean() * 100))
