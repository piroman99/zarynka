# -*- coding: utf-8 -*-
"""Где в новом фоне аллеи левый бордюр: замер по кадру, без гадания.

Метод: асфальт светлый и малонасыщенный, газон/хвоя темнее и зеленее. Для каждой
строки нижней половины кадра ищем самый сильный переход «тёмное -> светлое» в левой
трети, собираем точки и фитируем прямую (устойчиво, по медиане остатков).
Печатает: угол линии бордюра, её точки в пикселях 1920x1080 и точку, где ставить
скамейку 1.8 м на глубине anchor_y.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
W, H = 1920, 1080

im = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
lum = a.mean(axis=2)
mx = a.max(axis=2)
mn = a.min(axis=2)
sat = (mx - mn) / np.maximum(mx, 1.0)
# «дорожная» метрика: светло и не зелено
road = (lum / 255.0) * (1.0 - sat)

ys = np.arange(int(H * 0.55), int(H * 0.99), 4)
pts = []
for y in ys:
    row = road[y]
    # сгладим по x, чтобы не ловить зерно бумаги
    k = np.ones(9) / 9.0
    row_s = np.convolve(row, k, mode='same')
    # ищем максимум производной (переход газон->тротуар) в левой половине
    d = np.diff(row_s)
    lo, hi = int(W * 0.02), int(W * 0.55)
    seg = d[lo:hi]
    if seg.size == 0:
        continue
    # берём 3 кандидата и предпочитаем самый левый сильный (бордюр у газона)
    idx = np.argsort(seg)[::-1][:5]
    cand = sorted([lo + int(i) for i in idx])
    if not cand:
        continue
    x = cand[0]
    if seg.max() < 0.004:
        continue
    pts.append((x, int(y), float(seg.max())))

pts = np.array(pts, dtype=np.float64)
print('точек перехода:', len(pts))
if len(pts) < 20:
    raise SystemExit('мало точек — переход не найден')

# RANSAC по прямой x = a*y + b
rng = np.random.default_rng(7)
best = None
for _ in range(600):
    i, j = rng.integers(0, len(pts), 2)
    if abs(pts[i, 1] - pts[j, 1]) < 40:
        continue
    a1 = (pts[i, 0] - pts[j, 0]) / (pts[i, 1] - pts[j, 1])
    b1 = pts[i, 0] - a1 * pts[i, 1]
    res = np.abs(pts[:, 0] - (a1 * pts[:, 1] + b1))
    inl = res < 14
    score = inl.sum()
    if best is None or score > best[0]:
        best = (score, a1, b1, inl)
score, aa, bb, inl = best
print('RANSAC: inliers %d/%d, x = %.4f*y + %.1f' % (score, len(pts), aa, bb))
inl_x = pts[inl, 0]
inl_y = pts[inl, 1]
# МНК по инлайерам
A = np.vstack([inl_y, np.ones_like(inl_y)]).T
aa, bb = np.linalg.lstsq(A, inl_x, rcond=None)[0]
print('МНК:  x = %.4f*y + %.1f' % (aa, bb))

ang = np.degrees(np.arctan2(1.0, aa))       # наклон от горизонтали (по модулю)
print('угол линии бордюра от горизонтали: %.1f°' % abs(90 - ang))
for y in (1080, 950, 860, 780, 720, 660, 600):
    print('  y=%4d -> x=%6.1f' % (y, aa * y + bb))

# масштаб по глубине: m(y) = K*(y - y_h), калибровка по Екатерине (1.70 м, ступни y=1112)
Y_H = 572.0
M_REF = 619.0 / (1112.0 - Y_H)
print('\nмасштаб m(y) = %.4f*(y - %.0f) px/м' % (M_REF, Y_H))
for y in (860, 820, 780, 740, 700):

    m = M_REF * (y - Y_H)
    print('  y=%4d: %.0f px/м -> скамейка 1.8 м = %.0f px, спинка 0.90 м = %.0f px'
          % (y, m, 1.8 * m, 0.90 * m))
