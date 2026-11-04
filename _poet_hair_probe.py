# -*- coding: utf-8 -*-
"""Почему волосы вырезаны неровно: диагностика текущего cutout() на спрайтах поэта.

Считаем три вещи:
  1) ДЫРЫ — прозрачные области ВНУТРИ фигуры (замкнутые петли волос): текущий cutout —
     flood-fill ОТ КРАЯ, поэтому серый фон, замкнутый петлёй, остаётся залитым.
  2) ЗАЛИТЫЕ ПЕТЛИ — наоборот: пиксели цвета фона, оставшиеся непрозрачными внутри bbox.
  3) КАЙМА — непрозрачные пиксели у самой кромки, ещё близкие к цвету фона (серый ободок).
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(HERE, 'assets', 'sprites')

BG = np.array([205.0, 205.0, 205.0])


def cutout_old(im, tol=34):
    a = np.asarray(im.convert('RGB'), np.float32)
    h, w, _ = a.shape
    ring = np.concatenate([a[:8].reshape(-1, 3), a[:h * 3 // 5, :8].reshape(-1, 3),
                           a[:h * 3 // 5, -8:].reshape(-1, 3)])
    seed = np.median(ring, 0)
    cand = np.sqrt(((a - seed) ** 2).sum(2)) <= tol
    vis = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if cand[y, x] and not vis[y, x]:
                vis[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if cand[y, x] and not vis[y, x]:
                vis[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and cand[ny, nx] and not vis[ny, nx]:
                vis[ny, nx] = True
                dq.append((ny, nx))
    return a, vis


def components(mask):
    """Связные компоненты (4-связность) → список (площадь, bbox)."""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    out = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                dq = deque([(y, x)])
                seen[y, x] = True
                area = 0
                y0 = y1 = y
                x0 = x1 = x
                while dq:
                    cy, cx = dq.popleft()
                    area += 1
                    y0, y1 = min(y0, cy), max(y1, cy)
                    x0, x1 = min(x0, cx), max(x1, cx)
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            dq.append((ny, nx))
                out.append((area, (x0, y0, x1, y1)))
    return out


names = sys.argv[1:] or ['poet_ha_neutral', 'poet_ha_interested', 'poet_ha_upset',
                         'poet_sh_neutral', 'poet_sh_tired', 'poet_sh_inspired']

for n in names:
    p = os.path.join(SPR, n + '.png')
    if not os.path.exists(p):
        print('нет', p)
        continue
    a, transp = cutout_old(Image.open(p))
    h, w, _ = a.shape
    fig = ~transp
    ys, xs = np.nonzero(fig)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    # дыры: прозрачное, не касающееся края холста
    hole_mask = transp.copy()
    hole_mask[0, :] = hole_mask[-1, :] = False
    hole_mask[:, 0] = hole_mask[:, -1] = False
    comps = components(hole_mask)
    holes = [c for c in comps if c[0] >= 40]
    hole_area = sum(c[0] for c in holes)
    # залитые петли: НЕпрозрачное, но по цвету = фон
    d = np.abs(a - BG).max(2)
    filled_bg = fig & (d <= 22)
    # кайма: непрозрачное в 2 px от прозрачного, близкое к фону
    edge = np.zeros_like(fig)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            edge |= np.roll(np.roll(transp, dy, 0), dx, 1)
    fringe = fig & edge & (d <= 45)
    print('%-18s %4dx%-4d дыр(≥40px) %2d  площадь %5d px  залито фоном %5d px  кайма %5d px'
          % (n, w, h, len(holes), hole_area, int(filled_bg.sum()), int(fringe.sum())))
    if holes:
        big = sorted(holes, reverse=True)[:4]
        for area, bb in big:
            print('     петля %5d px в bbox %s' % (area, bb))
