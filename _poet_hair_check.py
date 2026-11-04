# -*- coding: utf-8 -*-
"""Замер «ровности» вырезания волос: серые пятна в петлях и серая кайма.

Метрики (меньше — лучше):
  СЕРЫЕ ПЯТНА  — непрозрачные (α>200) пиксели, цвет которых всё ещё в пределах d≤22 от фона.
                 Именно они читаются как «неровно вырезанные петли волос».
  КАЙМА        — полупрозрачные (0<α≤200) пиксели с d≤30 от фона: неперекрашенный серый ободок.
  ДЫРЫ         — замкнутые прозрачные области: это ПРАВИЛЬНЫЕ петли (сквозь них виден фон),
                 печатаем для справки.

Сравнивает СТАРУЮ вырезку (cutout() сборки: flood-fill от края, tol=34, blur 1.1)
и НОВУЮ (мягкая альфа + петли + despill).
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')
CH = os.path.join(HERE, 'vn2', 'img', 'char')

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
    return a, np.where(vis, 0.0, 1.0)


def metrics(rgb, alpha, bg=BG):
    h, w, _ = rgb.shape
    d = np.sqrt(((rgb - bg) ** 2).sum(2))
    solid = alpha > 0.78
    semi = (alpha > 0.02) & (alpha <= 0.78)
    grey_blob = solid & (d <= 22)
    fringe = semi & (d <= 30)
    # дыры: прозрачное, не связанное с краем холста
    hole = alpha <= 0.02
    hole[0, :] = hole[-1, :] = False
    hole[:, 0] = hole[:, -1] = False
    lab = 0
    seen = np.zeros_like(hole)
    for y in range(h):
        for x in range(w):
            if hole[y, x] and not seen[y, x]:
                dq = deque([(y, x)])
                seen[y, x] = True
                area = 0
                while dq:
                    cy, cx = dq.popleft()
                    area += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and hole[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            dq.append((ny, nx))
                if area >= 60:
                    lab += 1
    return dict(blob=int(grey_blob.sum()), fringe=int(fringe.sum()),
                semi=float(semi.mean()), holes=lab)


def find(name):
    for ext in ('.png', '.jpg'):
        p = os.path.join(GEN, 'poet_%s_0%s' % (name, ext))
        if os.path.exists(p):
            return p
    return None


FILES = ['ha_neutral', 'ha_interested', 'ha_upset', 'sh_neutral', 'sh_tired', 'sh_inspired']

print('%-14s | %-28s | %-28s' % ('', 'СТАРАЯ вырезка (в игре сейчас)', 'НОВАЯ (мягкая альфа)'))
print('%-14s | %7s %7s %7s %5s | %7s %7s %7s %5s'
      % ('спрайт', 'пятна', 'кайма', 'полупр', 'дыры', 'пятна', 'кайма', 'полупр', 'дыры'))
tot_old = tot_new = 0
for key in FILES:
    p = find(key)
    if not p:
        continue
    im = Image.open(p)
    rgb_o, a_o = cutout_old(im)
    mo = metrics(rgb_o, a_o)
    new_p = os.path.join(SPR, 'poet_%s_rgba.png' % key)
    if os.path.exists(new_p):
        im2 = Image.open(new_p)
        arr = np.asarray(im2, np.float32)
        rgb_n, a_n = arr[..., :3], arr[..., 3] / 255.0
        mn = metrics(rgb_n, a_n)
    else:
        mn = dict(blob=-1, fringe=-1, semi=0, holes=0)
    tot_old += mo['blob'] + mo['fringe']
    tot_new += max(0, mn['blob']) + max(0, mn['fringe'])
    print('%-14s | %7d %7d %6.1f%% %5d | %7d %7d %6.1f%% %5d'
          % (key, mo['blob'], mo['fringe'], 100 * mo['semi'], mo['holes'],
             mn['blob'], mn['fringe'], 100 * mn['semi'], mn['holes']))

print('\nсумма пятен+каймы: старая %d px, новая %d px (%.0f%% меньше)'
      % (tot_old, tot_new, 100 * (tot_old - tot_new) / max(1, tot_old)))

# что реально лежит в игре
wp = os.path.join(CH, 'poet.webp')
if os.path.exists(wp):
    im = Image.open(wp)
    arr = np.asarray(im.convert('RGBA'), np.float32)
    m = metrics(arr[..., :3], arr[..., 3] / 255.0)
    print('в игре poet.webp: пятна %d, кайма %d, полупрозрачных %.1f%%, дыр %d'
          % (m['blob'], m['fringe'], 100 * m['semi'], m['holes']))
