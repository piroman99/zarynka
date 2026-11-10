# -*- coding: utf-8 -*-
"""Нарисованная в фоне аллеи скамейка: точный bbox, окружение и чем её закрасить.

Печатаем вокруг пятна «дерева» (x 470..560, y 610..700 в фоне 1920x1080):
  • ASCII маски дерева в окне 380..760 x 540..820;
  • средний цвет пятна и цвет окружения (сверху / справа / слева) — чтобы понять,
    что там за текстура (асфальт, трава, бордюр) и откуда брать заплату.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'vn2', 'img', 'bg', 'alley.webp')
im = Image.open(P).convert('RGB')
W, H = im.size
a = np.asarray(im)
hsv = np.asarray(im.convert('HSV')).astype(np.int16)
Hc, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
wood = (Hc >= 6) & (Hc <= 32) & (S >= 55) & (V >= 45) & (V <= 210)

X0, X1, Y0, Y1 = 380, 760, 540, 820
print('окно x %d..%d y %d..%d, доля «дерева» в окне %.2f%%'
      % (X0, X1, Y0, Y1, 100 * wood[Y0:Y1, X0:X1].mean()))
sub = wood[Y0:Y1, X0:X1]
cols, rows = 76, 40
for r in range(rows):
    line = []
    for c in range(cols):
        ya, yb = int(r * sub.shape[0] / rows), int((r + 1) * sub.shape[0] / rows)
        xa, xb = int(c * sub.shape[1] / cols), int((c + 1) * sub.shape[1] / cols)
        f = sub[ya:yb, xa:xb].mean()
        line.append('#' if f > 0.5 else ('+' if f > 0.2 else ('.' if f > 0.05 else ' ')))
    print('|' + ''.join(line) + '|  y=%d' % (Y0 + int(r * sub.shape[0] / rows)))

# точный bbox пятна внутри окна
ys, xs = np.nonzero(sub)
if len(xs):
    print('\nbbox пятна: x %d..%d  y %d..%d'
          % (X0 + xs.min(), X0 + xs.max(), Y0 + ys.min(), Y0 + ys.max()))

# цвета окружения
def mean_rgb(x0, x1, y0, y1):
    return a[y0:y1, x0:x1].reshape(-1, 3).mean(0).round().astype(int)

bx0, bx1, by0, by1 = X0 + xs.min(), X0 + xs.max(), Y0 + ys.min(), Y0 + ys.max()
print('\nцвет пятна      :', mean_rgb(bx0, bx1 + 1, by0, by1 + 1))
print('сверху 60 px    :', mean_rgb(bx0, bx1 + 1, max(0, by0 - 60), by0))
print('снизу 60 px     :', mean_rgb(bx0, bx1 + 1, by1 + 1, min(H, by1 + 61)))
print('слева 120 px    :', mean_rgb(max(0, bx0 - 120), bx0, by0, by1 + 1))
print('справа 120 px   :', mean_rgb(bx1 + 1, min(W, bx1 + 121), by0, by1 + 1))
print('пятно %dx%d в фоне %dx%d (%.2f%% кадра)'
      % (bx1 - bx0 + 1, by1 - by0 + 1, W, H,
         100.0 * (bx1 - bx0 + 1) * (by1 - by0 + 1) / (W * H)))
