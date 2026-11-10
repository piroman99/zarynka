# -*- coding: utf-8 -*-
"""Точка схода аллеи: куда уходит дорожка. От этого зависит, под каким углом должна
стоять скамейка (её длинная ось параллельна дорожке -> смотрит в ту же точку схода).

Метод: идём по строкам снизу вверх и ищем границу «асфальт | не асфальт» слева и справа
(асфальт светлый и малонасыщенный, трава/ели тёмные и/или зелёные). К найденным точкам
подгоняем прямые; их пересечение — точка схода.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'vn2', 'img', 'bg', 'alley.webp')).convert('RGB')
a = np.asarray(im).astype(np.float32)
W, H = im.size
hsv = np.asarray(im.convert('HSV')).astype(np.int16)
Hc, S, V = hsv[..., 0].astype(np.float32), hsv[..., 1].astype(np.float32), hsv[..., 2]
lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

# асфальт: светлый (V>110), не зелёный (не 40..110 в PIL-H), насыщенность низкая/средняя
asphalt = (V > 105) & (S < 90) & ~((Hc > 38) & (Hc < 115) & (S > 60))
print('доля «асфальта»: %.1f%%' % (100 * asphalt.mean()))

left_pts, right_pts = [], []
for y in range(int(H * 0.55), H, 4):
    row = asphalt[y]
    # сглаживаем строку по 9 px, чтобы не ловить одиночные мазки
    k = np.ones(9) / 9.0
    sm = np.convolve(row.astype(np.float32), k, mode='same')
    on = sm > 0.6
    if on.sum() < 40:
        continue
    idx = np.nonzero(on)[0]
    # самая длинная непрерывная полоса
    splits = np.nonzero(np.diff(idx) > 1)[0]
    segs = np.split(idx, splits + 1)
    seg = max(segs, key=len)
    if len(seg) < 80:
        continue
    left_pts.append((seg[0], y))
    right_pts.append((seg[-1], y))

print('точек границы: слева %d, справа %d' % (len(left_pts), len(right_pts)))
for name, pts in (('левый край', left_pts), ('правый край', right_pts)):
    if len(pts) < 10:
        print('%s: мало точек' % name)
        continue
    p = np.array(pts, float)
    # отбрасываем выбросы по x (медианный фильтр по y)
    med = np.median(p[:, 0])
    keep = np.abs(p[:, 0] - med) < 0.28 * W
    p = p[keep]
    kk, bb = np.polyfit(p[:, 1], p[:, 0], 1)
    ang = np.degrees(np.arctan(kk))
    print('%s: x = %.4f y + %.1f  -> наклон к вертикали %.1f°  (точек %d, y %d..%d)'
          % (name, kk, bb, ang, len(p), p[:, 1].min(), p[:, 1].max()))
    if name == 'левый край':
        kL, bL = kk, bb
    else:
        kR, bR = kk, bb

if abs(kL - kR) > 1e-6:
    yv = (bR - bL) / (kL - kR)
    xv = kL * yv + bL
    print('\nТОЧКА СХОДА: x=%.0f (%.0f%% ширины), y=%.0f (%.0f%% высоты)'
          % (xv, 100 * xv / W, yv, 100 * yv / H))
    for label, bx, by in (('скамейка слева (x 20%%, y 90%%)', 0.20 * W, 0.90 * H),
                          ('скамейка (x 30%%, y 88%%)', 0.30 * W, 0.88 * H)):
        dx, dy = xv - bx, yv - by
        ang = np.degrees(np.arctan2(-dy, dx))
        print('  %s -> длинная ось должна идти под %+.1f° (плюс = вверх-вправо), длина %.0f px'
              % (label, ang, np.hypot(dx, dy)))
