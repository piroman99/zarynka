# -*- coding: utf-8 -*-
"""Форма лого в кадре перехода: круг или квадрат? Смотрим УГЛЫ рамки вокруг лого.

Квадратное лого давало светлые углы (белый фон исходника), круглое — тёмные углы
и светлую середину. Проверка числом, без глаз:
  * bbox светлого пятна (должен быть ~квадратным по размеру, но);
  * яркость 4 углов bbox (квадрат = ярко, круг = темно);
  * доля ярких пикселей внутри bbox (круг ≈ 0.785, квадрат ≈ 1.0).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'assets', 'review', 'review_115_trans_logo.png')
im = np.asarray(Image.open(p).convert('L'), dtype=np.float32) / 255.0
h, w = im.shape
y0, y1, x0, x1 = int(h * .25), int(h * .75), int(w * .25), int(w * .75)
c = im[y0:y1, x0:x1]
mask = c > 0.30
ys, xs = np.nonzero(mask)
if not len(ys):
    raise SystemExit('лого не видно')
bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
bw, bh = bx1 - bx0 + 1, by1 - by0 + 1
pad = 3
corners = [c[by0 + pad, bx0 + pad], c[by0 + pad, bx1 - pad],
           c[by1 - pad, bx0 + pad], c[by1 - pad, bx1 - pad]]
fill = mask[by0:by1 + 1, bx0:bx1 + 1].mean()
print('лого: bbox %dx%d, центр (%d, %d)' % (bw, bh, x0 + (bx0 + bx1) // 2,
                                           y0 + (by0 + by1) // 2))
print('углы bbox: %.3f %.3f %.3f %.3f  (квадрат -> ~0.8, круг -> ~0.03)'
      % tuple(corners))
print('заполнение bbox: %.1f%%  (круг ~78.5%%, квадрат ~100%%)' % (fill * 100))
ok = max(corners) < 0.25 and fill < 0.90
print('ИТОГ: ' + ('КРУГ — квадратных углов нет' if ok else 'ПОХОЖЕ НА КВАДРАТ'))
