# -*- coding: utf-8 -*-
"""Проверка самих кропов сетки: каждый ли сидит на краю силуэта и ушла ли кайма.

Для каждого спрайта берётся тот же кроп, что в _defringe_grid.py, и считается
яркость внешнего кольца силуэта против кольца 2..5 px внутри — отдельно ДО и ПОСЛЕ.
"""
import io
import os
import subprocess

import numpy as np
from PIL import Image

import _defringe_grid as g

CHAR = g.CHAR
Z = g.Z


def erode(mask, n=1):
    m = mask.copy()
    for _ in range(n):
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        m = e
    return m


def rim(part):
    a = np.asarray(part)[:, :, 3]
    rgb = np.asarray(part)[:, :, :3].astype(np.float32)
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    solid = a > 200
    clear = a < 20
    if solid.sum() < 200 or clear.sum() < 200:
        return None
    r0 = solid & ~erode(solid, 1)
    r1 = erode(solid, 2) & ~erode(solid, 5)
    if not r1.any():
        return None
    return float(lum[r0].mean() - lum[r1].mean()), float(solid.mean())


print('%-28s %-26s %-26s %s' % ('файл', 'кроп ДО: Δкаймы/плотн.', 'кроп ПОСЛЕ: Δкаймы/плотн.', 'итог'))
ok_all = True
for name in g.NAMES:
    before = g.load_ref(name)
    after = Image.open(os.path.join(CHAR, name)).convert('RGBA')
    box = g.fringe_box(np.asarray(before))
    if box is None:
        print('%-28s нет кластера кромки' % name)
        ok_all = False
        continue
    cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
    x0 = max(0, min(before.width - Z, cx - Z // 2))
    y0 = max(0, min(before.height - Z, cy - Z // 2))
    cb = before.crop((x0, y0, x0 + Z, y0 + Z))
    ca = after.crop((x0, y0, x0 + Z, y0 + Z))
    rb, ra = rim(cb), rim(ca)
    if rb is None or ra is None:
        print('%-28s кроп не на краю (нет и прозрачного, и плотного)' % name)
        ok_all = False
        continue
    verdict = 'OK' if (rb[0] > 8 and ra[0] < 8) else '!!!'
    if verdict != 'OK':
        ok_all = False
    print('%-28s %+6.1f / %4.2f          %+6.1f / %4.2f          %s'
          % (name, rb[0], rb[1], ra[0], ra[1], verdict))
print('\nвсе кропы годные: %s' % ok_all)
