# -*- coding: utf-8 -*-
"""Аккуратное матирование спрайта: мягкая альфа по цвету фона + снятие серой каймы.

ПОЧЕМУ ПРЕЖНЯЯ ВЫРЕЗКА БЫЛА НЕРОВНОЙ (это вопрос Ивана 2026-11-04):
в сборке стоит `cutout()` — flood-fill ОТ КРАЯ холста по цветовой близости к фону
(tol=34) плюс размытие альфы 1.1 px. Три следствия:
  1) фон, ЗАМКНУТЫЙ петлёй волос, до края не достаётся → остаётся непрозрачным серым
     пятном между прядями (в кадре это и видно как «неровно вырезанные петли»);
  2) бинарная альфа + размытие = серая кайма по контуру (полупрозрачные пиксели,
     сохранившие цвет фона), на тёмных волосах она читается особенно сильно;
  3) webp пишется с потерями → кайма «звенит».

Здесь правильный маттинг:
  • мягкая альфа по расстоянию до цвета фона (A0..A1), а не бинарная;
  • ЛЮБАЯ замкнутая область цвета фона площадью ≤ HOLE_MAX считается фоном
    (петли волос), даже если она не связана с краем холста;
  • despill: у полупрозрачных пикселей вычитаем вклад фона по альфе
    (c = (c_obs − (1−a)·bg) / a) — серая кайма исчезает;
  • фон холста делаем ПРОЗРАЧНЫМ (RGBA), и сборка такие файлы больше не режет.

Запуск: python3 _poet_matte.py [имена]
Проверка: python3 _poet_hair_check.py
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')

A0, A1 = 12.0, 40.0      # рампа альфы: d≤A0 — чистый фон, d≥A1 — чистый персонаж
# Пороги безопасны: замер `_poet_thresh_probe.py` даёт чёткую дыру между фоном (d≈0–3)
# и фигурой (20-й перцентиль d≈45), светлая рубашка тоже d>45 — в зону фона не попадает.
HOLE_MAX = 60000         # замкнутая область фона больше этого — не петля, оставляем
DESPILL = True


def label(mask):
    """Связные компоненты 4-связностью. Возвращает (labels int32, n).

    Реализация через union-find по строчным пробегам: на 1.8 Мпикс работает секунды,
    scipy в песочнице нет.
    """
    h, w = mask.shape
    parent = []

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    row_runs = []
    for y in range(h):
        row = mask[y]
        if not row.any():
            row_runs.append([])
            continue
        idx = np.nonzero(np.diff(np.concatenate(([0], row.view(np.int8), [0]))))[0]
        runs = []
        for i in range(0, len(idx), 2):
            x0, x1 = int(idx[i]), int(idx[i + 1]) - 1
            rid = len(parent)
            parent.append(rid)
            runs.append((x0, x1, rid))
        row_runs.append(runs)

    for y in range(1, h):
        prev, cur = row_runs[y - 1], row_runs[y]
        j = 0
        for x0, x1, rid in cur:
            while j < len(prev) and prev[j][1] < x0:
                j += 1
            k = j
            while k < len(prev) and prev[k][0] <= x1:
                union(rid, prev[k][2])
                k += 1

    labels = np.zeros((h, w), np.int32)
    for y in range(h):
        for x0, x1, rid in row_runs[y]:
            labels[y, x0:x1 + 1] = find(rid) + 1
    return labels, len(parent)


def matte(im):
    a = np.asarray(im.convert('RGB'), np.float32)
    h, w, _ = a.shape
    ring = np.concatenate([a[:8].reshape(-1, 3),
                           a[:int(h * 0.6), :8].reshape(-1, 3),
                           a[:int(h * 0.6), -8:].reshape(-1, 3)])
    bg = np.median(ring, 0)
    d = np.sqrt(((a - bg) ** 2).sum(2))

    # 1) области, «заведомо фон» (строгий порог — иначе рампа альфы вырождается в бинарную)
    bgish = d <= A0
    lab, n = label(bgish)
    border_ids = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist())
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    bgmask = np.zeros((h, w), bool)
    for lid in np.unique(lab):
        if lid == 0:
            continue
        if lid in border_ids or sizes[lid] <= HOLE_MAX:
            bgmask |= (lab == lid)          # фон с края ИЛИ замкнутая петля волос
    # 2) мягкая альфа
    ramp = np.clip((d - A0) / (A1 - A0), 0.0, 1.0)
    alpha = np.where(bgmask, 0.0, ramp)
    alpha[d >= A1] = 1.0
    # 3) despill: снимаем вклад фона у полупрозрачных пикселей
    if DESPILL:
        a3 = alpha[..., None]
        safe = np.maximum(a3, 0.15)
        unmixed = (a - (1.0 - a3) * bg) / safe
        mixed = (alpha > 0.02) & (alpha < 0.98)
        out = np.where(mixed[..., None], np.clip(unmixed, 0, 255), a)
    else:
        out = a
    rgba = np.dstack([out, alpha * 255.0]).round().astype(np.uint8)
    stats = dict(bg=bg.round().astype(int).tolist(),
                 removed=float(bgmask.mean()),
                 soft=float(((alpha > 0.02) & (alpha < 0.98)).mean()))
    return Image.fromarray(rgba, 'RGBA'), stats


def find(name):
    for ext in ('.png', '.jpg'):
        p = os.path.join(GEN, 'poet_%s_0%s' % (name, ext))
        if os.path.exists(p):
            return p
    return None


FILES = ['ha_neutral', 'ha_interested', 'ha_upset',
         'sh_neutral', 'sh_tired', 'sh_inspired']

if __name__ == '__main__':
    only = sys.argv[1:]
    print('матирование поэта -> assets/sprites/poet_*_rgba.png')
    for key in FILES:
        if only and key not in only:
            continue
        p = find(key)
        if not p:
            print('  нет', key)
            continue
        im, st = matte(Image.open(p))
        out = os.path.join(SPR, 'poet_%s_rgba.png' % key)
        im.save(out)
        print('  %-14s фон %s  фон снят %.0f%%  мягкий край %.1f%%  -> %s'
              % (key, st['bg'], 100 * st['removed'], 100 * st['soft'], os.path.basename(out)))
