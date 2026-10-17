# -*- coding: utf-8 -*-
"""Проверка правки S4 (v2): ищем САМ ТЕКСТ по цвету CREAM, потом скрим вокруг."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets/final/prolog/s4.png')).convert('RGB')
W, H = im.size
a = np.asarray(im).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
# CREAM (246,238,222): почти белый, тёплый, r>g>b
m = (r > 205) & (g > 195) & (b > 175) & (r - b > 12) & (r - b < 40) & (np.abs(r - g) < 16)
ys, xs = np.nonzero(m)
print('cream px n=%d' % len(xs))
# отбрасываем лампу/иные светлые пятна: берём только полосу ниже ТВ (y>500)
keep = (ys > 500) & (ys < 700)
ys2, xs2 = ys[keep], xs[keep]
print('text bbox:', xs2.min(), ys2.min(), xs2.max(), ys2.max(),
      'size %dx%d' % (xs2.max() - xs2.min() + 1, ys2.max() - ys2.min() + 1))

y0, y1 = ys2.min(), ys2.max()
x0, x1 = xs2.min(), xs2.max()
# скрим: тёмные пиксели той же полосы
sub = a[y0 - 40:y1 + 40, x0 - 80:x1 + 80]
sl = sub @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
dys, dxs = np.nonzero(sl < 60)
print('scrim bbox:', x0 - 80 + dxs.min(), y0 - 40 + dys.min(), x0 - 80 + dxs.max(), y0 - 40 + dys.max())
print('scrim alpha-est: median lum внутри =', round(float(np.median(sl[dys, dxs])), 1))


def proj(v, o, s):
    return o + (v - o) * s


print('\n--- проекция наезда (1.0 -> 1.5, origin x .44 y .30) ---')
for nm, yv in (('scrim top', y0 - 40), ('scrim bottom', y1 + 40),
               ('text top', y0), ('text bottom', y1)):
    print('%-12s y=%.3f -> %.3f' % (nm, yv / H, proj(yv / H, 0.30, 1.5)))
print('видимая область наезда: y 0.100..0.767, x 0.147..0.813')
print('текст по x: %.3f..%.3f -> на наезде %.3f..%.3f' % (
    x0 / W, x1 / W, proj(x0 / W, 0.44, 1.5), proj(x1 / W, 0.44, 1.5)))
