# -*- coding: utf-8 -*-
"""Проверка нормировки эмоций поэта: плечи/холст одинаковые, низ фигуры на кромке.

Файлы — RGB на светло-сером фоне (вырезку делает сборка), поэтому маска = пиксели,
далёкие от цвета фона (205,205,205).

Эталон — Сергей: плечи/холст 0.559. Допуск ±0.012 (иначе в движке «прыгнет» голова).
Плюс: низ фигуры на нижней кромке холста (±8 px) — иначе спрайт «всплывёт» над полом.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(HERE, 'assets', 'sprites')

TARGET = 0.56
TOL = 0.012
NAMES = sys.argv[1:] or ['poet_ha_neutral', 'poet_ha_interested', 'poet_ha_upset',
                         'poet_sh_neutral', 'poet_sh_tired', 'poet_sh_inspired']


def mask_of(im):
    if im.mode == 'RGBA':
        return np.asarray(im.split()[-1]) > 128
    a = np.asarray(im.convert('RGB'), np.int16)
    return np.abs(a - np.array([205, 205, 205])).max(2) > 24


ok = fail = 0
for n in NAMES:
    p = os.path.join(SPR, n + '.png')
    if not os.path.exists(p):
        print('FAIL нет файла', n)
        fail += 1
        continue
    im = Image.open(p)
    m = mask_of(im)
    ys, xs = np.nonzero(m)
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0
    band = m[y0 + int(bh * 0.35):y0 + int(bh * 0.55)]
    cols = np.nonzero(band.any(0))[0]
    sh = int(cols.max() - cols.min()) if len(cols) else 0
    r = sh / im.height
    near_bottom = abs(y1 - (im.height - 1)) <= 8
    good = abs(r - TARGET) <= TOL and near_bottom
    ok += good
    fail += (not good)
    print('%s %-20s %s  плечи/H %.3f  низ %4d/%4d  фигура %.0f%% кадра'
          % ('OK  ' if good else 'FAIL', n, im.size, r, y1, im.height - 1,
             100 * float(m.mean())))

print('\nИТОГ: OK=%d FAIL=%d' % (ok, fail))
sys.exit(1 if fail else 0)
