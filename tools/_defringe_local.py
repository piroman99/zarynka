# -*- coding: utf-8 -*-
"""Локальный тест: полупрозрачная бахрома против ПЛОТНОГО тела РЯДОМ (окно 9x9).

Средняя по всему спрайту яркость тела обманывает: у «сидящих» поэтов рядом кожа
и блики, они светлее среднего. Здесь для каждого пикселя бахромы берётся среднее
по плотным соседям в окне 9x9 — то есть «что лежит прямо за кромкой».
Кайма = бахрома заметно светлее своего окружения.
"""
import io
import os
import subprocess

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')
REF = os.environ.get('REF', '0e50695')
WIN = 9

NAMES = [
    'poet.webp', 'poet_interested.webp', 'poet_upset.webp',
    'poet_seat.webp', 'poet_seat_interested.webp', 'poet_seat_shy.webp',
    'poet_seat_smile.webp', 'poet_seat_sullen.webp', 'poet_seat_upset.webp',
    'poet_sh.webp', 'poet_sh_inspired.webp', 'poet_sh_tired.webp',
    'poet_sit.webp', 'poet_sit_interested.webp', 'poet_sit_upset.webp',
    'sergey.webp', 'sergey_concerned.webp', 'sergey_smile.webp',
]


def load_ref(name):
    raw = subprocess.check_output(['git', 'show', REF + ':vn2/img/char/' + name], cwd=ROOT)
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))


def box_mean(vals, weights, win):
    """среднее vals по окну win×win, взвешенное weights (только плотные)."""
    r = win // 2
    v = np.pad(vals * weights, r, mode='constant')
    w = np.pad(weights.astype(np.float32), r, mode='constant')
    # интегральные суммы
    cv = v.cumsum(0).cumsum(1)
    cw = w.cumsum(0).cumsum(1)
    cv = np.pad(cv, ((1, 0), (1, 0)))
    cw = np.pad(cw, ((1, 0), (1, 0)))
    k = win
    sv = cv[k:, k:] - cv[:-k, k:] - cv[k:, :-k] + cv[:-k, :-k]
    sw = cw[k:, k:] - cw[:-k, k:] - cw[:-k, :] if False else (
        cw[k:, k:] - cw[:-k, k:] - cw[k:, :-k] + cw[:-k, :-k])
    with np.errstate(invalid='ignore', divide='ignore'):
        out = np.where(sw > 0.5, sv / sw, np.nan)
    return out[:vals.shape[0], :vals.shape[1]]


def local_gap(arr):
    a = arr[:, :, 3].astype(np.float32)
    rgb = arr[:, :, :3].astype(np.float32)
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    band = (a > 20) & (a < 200)
    solid = (a > 245).astype(np.float32)
    if band.sum() < 50:
        return None
    loc = box_mean(lum, solid, WIN)
    g = lum[band] - loc[band]
    g = g[np.isfinite(g)]
    if not g.size:
        return None
    return float(g.mean()), float(np.median(g)), float((g > 25).mean() * 100), int(g.size)


print('%-28s %-30s %-30s %s'
      % ('файл', 'ДО: зазор ср/медиана/%>25', 'ПОСЛЕ: зазор ср/медиана/%>25', 'итог'))
bad = []
for n in NAMES:
    b = local_gap(load_ref(n))
    a = local_gap(np.asarray(Image.open(os.path.join(CHAR, n)).convert('RGBA')))
    if b is None or a is None:
        print('%-28s нет данных' % n)
        continue
    ok = a[1] < 12
    if not ok:
        bad.append(n)
    print('%-28s %+6.1f / %+6.1f / %4.1f %%        %+6.1f / %+6.1f / %4.1f %%        %s'
          % (n, b[0], b[1], b[2], a[0], a[1], a[2], 'OK' if ok else '!!! ПРОВЕРИТЬ'))
print('\nпроблемных: %d %s' % (len(bad), bad if bad else ''))
