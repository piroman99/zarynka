# -*- coding: utf-8 -*-
"""Сводка по всем спрайтам персонажей: у кого есть светлая кайма по краю."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')


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


print('%-30s %8s %8s %8s %6s' % ('файл', 'ядро', 'кромка', 'бахрома', 'кайма'))
for name in sorted(os.listdir(CHAR)):
    if not name.endswith('.webp'):
        continue
    arr = np.asarray(Image.open(os.path.join(CHAR, name)).convert('RGBA')).astype(float)
    rgb, al = arr[:, :, :3], arr[:, :, 3]
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    solid = al > 128
    if not solid.any():
        continue
    edge = solid & ~erode(solid, 2)
    core = lum[al > 230].mean()
    fr = (al > 20) & (al <= 180)
    halo = (edge & (lum > core + 40)).sum()
    print('%-30s %8.1f %8.1f %8.1f %6d %s'
          % (name, core, lum[edge].mean(), lum[fr].mean() if fr.any() else -1, halo,
             '<== кайма' if halo > 500 else ''))
