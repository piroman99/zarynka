# -*- coding: utf-8 -*-
"""Насколько сборка изменила спрайты относительно HEAD: внутри (глубже 6 px) должно
быть |Δ| = 0, снаружи — только кромка. Печатает по файлу: размеры, внутреннее Δ,
долю видимых пикселей с Δ > 8 и где они лежат (расстояние от кромки).

Запуск: python3 tools/_char_vs_head.py
"""
import io
import os
import subprocess

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')


def erode(m, n):
    for _ in range(n):
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        m = e
    return m


rows = []
for name in sorted(os.listdir(CHAR)):
    if not name.endswith('.webp'):
        continue
    head = subprocess.run(['git', 'show', 'HEAD:vn2/img/char/' + name],
                          cwd=ROOT, capture_output=True).stdout
    if not head:
        continue
    a = np.asarray(Image.open(io.BytesIO(head)).convert('RGBA'), np.int16)
    b = np.asarray(Image.open(os.path.join(CHAR, name)).convert('RGBA'), np.int16)
    if a.shape != b.shape:
        print('%-26s РАЗМЕР %s -> %s' % (name, a.shape, b.shape))
        continue
    d = np.abs(a - b).max(axis=2)
    if d.max() == 0:
        continue
    deep = erode(a[:, :, 3] > 250, 6) & erode(b[:, :, 3] > 250, 6)
    vis = (a[:, :, 3] > 40) | (b[:, :, 3] > 40)
    near = erode(vis, 2)
    print('%-26s %7d->%7d B | внутри max %3d ср %5.2f | видимых Δ>8: %6d (%.1f%%), '
          'из них глубже 2 px от кромки: %d'
          % (name, len(head), os.path.getsize(os.path.join(CHAR, name)),
             d[deep].max() if deep.any() else -1, d[deep].mean() if deep.any() else -1,
             int(((d > 8) & vis).sum()), 100.0 * ((d > 8) & vis).sum() / max(1, vis.sum()),
             int(((d > 8) & near).sum())))
