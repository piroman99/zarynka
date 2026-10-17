# -*- coding: utf-8 -*-
"""Проверка кандидатов раскладки значка-видео.

1) буквы не касаются жетона — bbox'ы из ПИКСЕЛЕЙ (кадр с титулом минус кадр без),
2) фон градиентный (альфа работает),
3) ширина перехода на краю жетона: старый кадр (1280/текстура 256) vs новый
   (1920/текстура 1024, сс2) при одном размере жетона.
"""
import os
import numpy as np
from PIL import Image

import _zn3d_hi as HZ

R = HZ.REVIEW
W, H = 1920, 1080
CANDS = [('A', 290, 430, 170, 800), ('B', 320, 440, 150, 830), ('C', 290, 560, 170, 100)]


def arr(im):
    return np.asarray(im.convert('RGB')).astype(np.float32)


def bbox(mask):
    ys, xs = np.where(mask)
    if not len(ys):
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()


def edge_width(prof):
    """Ширина перехода 10-90 % по профилю яркости (px)."""
    lo, hi = np.percentile(prof, 3), np.percentile(prof, 97)
    t10, t90 = lo + 0.1 * (hi - lo), lo + 0.9 * (hi - lo)
    i10 = next((i for i, v in enumerate(prof) if v > t10), None)
    i90 = next((i for i, v in enumerate(prof) if v > t90), None)
    if i10 is None or i90 is None:
        return float('nan')
    return abs(i90 - i10)


print('--- буквы vs жетон (bbox из пикселей) ---')
res = {}
for name, r, cy, tp, ty in CANDS:
    with_t, _ = HZ.frame(W, H, 180.0, r, cy, tp, ty, title=True)
    no_t, _ = HZ.frame(W, H, 180.0, r, cy, tp, ty, title=False)
    a, b = arr(with_t), arr(no_t)
    tb = bbox(b.astype(np.uint8).max(axis=2) > 70)          # жетон: яркие/цветные пиксели
    d = np.abs(a - b).mean(axis=2) > 6                       # буквы: разница с кадром без титула
    yb = bbox(d)
    gap = None
    if yb[1] > tb[3]:
        gap = yb[1] - tb[3]
    elif tb[1] > yb[3]:
        gap = tb[1] - yb[3]
    else:
        gap = -1
    res[name] = (tb, yb, gap)
    print('%s: жетон x %d..%d y %d..%d | титул x %d..%d y %d..%d | зазор %s px  %s'
          % (name, tb[0], tb[2], tb[1], tb[3], yb[0], yb[2], yb[1], yb[3], gap,
             'OK' if gap > 25 else 'ТЕСНО/ПЕРЕКРЫТИЕ'))

print('\n--- фон: углы ---')
for name in ('A', 'B', 'C'):
    a = arr(Image.open(os.path.join(R, '_zn2_%s_180.png' % name)))
    print('%s: %s / %s (старый кадр: плоские 6,8,18 во всех трёх)'
          % (name, a[6, 6].round(0), a[-6, -6].round(0)))

print('\n--- ширина перехода на левом ребре жетона (меньше = резче) ---')
old = arr(Image.open(os.path.join(R, '_znchek_4.9.png')))
prof_old = old.mean(axis=2)[336, 380:440]                    # центр жетона, через левый край
print('старый (1280x720, текстура 256): %.1f px' % edge_width(prof_old))

for name, r, cy, tp, ty in CANDS:
    new = arr(Image.open(os.path.join(R, '_zn2_%s_180.png' % name)))
    cx = W // 2
    left = int(cx - 1.902 * r / 2)                            # левый край пятиугольника
    prof = new.mean(axis=2)[int(cy), left - 30:left + 30]
    print('%s (1920x1080, текстура 1024, сс2): %.1f px' % (name, edge_width(prof)))

print('\n--- сколько пикселей на единицу текстуры ---')
print('старый: текстурная грань 256 px -> на экране грань ~478 px = %.2fx растяжение' % (478 / 256))
print('новый A: текстура 1024 px -> грань 552 px = %.2fx (запас деталей)' % (552 / 1024))
print('к тому же старый кадр 1280 широкий: на 1920-экране ещё 1.5x')
