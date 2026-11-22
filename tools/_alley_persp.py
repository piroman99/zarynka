# -*- coding: utf-8 -*-
"""ЗАМЕР: под каким углом должна стоять скамейка в сцене «аллея».

Три независимых числа:
  1) нарисованная в фоне скамейка (её длинная ось по маске «дерево», PCA) — это та,
     что «торчит из-под пропа»; модель нарисовала её в правильной перспективе;
  2) точка схода аллеи: пересечение левой и правой линии бордюра;
  3) угол от площадки у пропа к точке схода — под ним должна уходить длина скамейки.

Печатаем углы в градусах (плюс = против часовой на экране, то есть дальний конец выше).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'vn2', 'img', 'bg', 'alley.webp')

im = Image.open(P).convert('RGB')
W0, H0 = im.size
print('фон %dx%d' % (W0, H0))


def axis_angle(mask):
    ys, xs = np.nonzero(mask)
    xs = xs.astype(np.float64)
    ys = ys.astype(np.float64)
    xs -= xs.mean()
    ys -= ys.mean()
    cov = np.cov(np.vstack([xs, ys]))
    ev, evec = np.linalg.eigh(cov)
    v = evec[:, np.argmax(ev)]
    ang = np.degrees(np.arctan2(-v[1], v[0]))   # минус: экранный y вниз
    if ang > 90:
        ang -= 180
    if ang < -90:
        ang += 180
    return ang, len(xs)


# ---------- 1) нарисованная скамейка в фоне ----------
hsv = np.asarray(im.convert('HSV')).astype(np.int16)
Hc, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
wood = (Hc >= 6) & (Hc <= 32) & (S >= 45) & (V >= 45) & (V <= 215)
region = np.zeros_like(wood)
region[int(0.72 * H0):int(0.95 * H0), 0:int(0.22 * W0)] = True
m = wood & region
ang, n = axis_angle(m)
print('\nнарисованная скамейка в фоне (низ-лево, %d точек): ось %.1f°' % (n, ang))
ys, xs = np.nonzero(m)
print('  bbox x %d..%d (%.1f..%.1f%%)  y %d..%d (%.1f..%.1f%%)'
      % (xs.min(), xs.max(), 100.0 * xs.min() / W0, 100.0 * xs.max() / W0,
         ys.min(), ys.max(), 100.0 * ys.min() / H0, 100.0 * ys.max() / H0))

# ---------- 2) точка схода по бордюрам ----------
rgb = np.asarray(im).astype(np.float32)
lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
# дорожка светлее травы: для каждой колонки ищем нижнюю границу «светлого»
bright = lum > np.percentile(lum, 55)
edges = []
for x in range(0, W0, 8):
    col = bright[:, x]
    idx = np.nonzero(col)[0]
    if len(idx) < 10:
        continue
    # самый нижний переход светлое -> тёмное
    last = idx.max()
    if last < H0 - 4:
        edges.append((x, last))
edges = np.array(edges, dtype=np.float64)
print('\nточек края дорожки: %d' % len(edges))


def fit(sel, label):
    if len(sel) < 12:
        print('  %s: мало точек' % label)
        return None
    x = sel[:, 0]
    y = sel[:, 1]
    # робастно: две итерации по остаткам
    k, b = np.polyfit(x, y, 1)
    for _ in range(3):
        r = np.abs(y - (k * x + b))
        keep = r < max(np.percentile(r, 70), 4)
        if keep.sum() < 12:
            break
        k, b = np.polyfit(x[keep], y[keep], 1)
    print('  %s: y = %.4f x + %.1f  (наклон %.1f°, точек %d)'
          % (label, k, b, -np.degrees(np.arctan(k)), keep.sum()))
    return k, b


left = fit(edges[edges[:, 0] < W0 * 0.45], 'левый край')
right = fit(edges[edges[:, 0] > W0 * 0.55], 'правый край')
if left and right:
    k1, b1 = left
    k2, b2 = right
    if abs(k1 - k2) > 1e-4:
        xv = (b2 - b1) / (k1 - k2)
        yv = k1 * xv + b1
        print('\nточка схода: x %.0f (%.1f%%), y %.0f (%.1f%%)'
              % (xv, 100.0 * xv / W0, yv, 100.0 * yv / H0))
    else:
        xv = yv = None
        print('\nбордюры параллельны — точки схода нет')

    # ---------- 3) угол от площадки скамейки к точке схода ----------
    # площадка пропа: left 22 %, bottom -6 % сцены 1346x757 при фоне 1:1
    STAGE_W, STAGE_H = 1346.0, 757.0
    scale = W0 / STAGE_W
    bx = (0.22 * STAGE_W) * scale
    by = (STAGE_H * 1.06) * scale
    print('площадка пропа в пикселях фона: x %.0f, y %.0f' % (bx, by))
    if xv is not None:
        dx, dy = xv - bx, yv - by
        print('направление к точке схода: dx %.0f dy %.0f -> угол %.1f° к горизонту'
              % (dx, dy, np.degrees(np.arctan2(-dy, dx))))
