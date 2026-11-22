# -*- coding: utf-8 -*-
"""Собственный угол пропа bench: PCA по маске + профиль «где доски».

Нужно понять, под каким углом сама нарисованная скамейка уходит в глубину: если угол
уже близок к перспективе аллеи, поворачивать проп нельзя вообще (иначе «завал»).
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
P = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)
m = a[:, :, 3] > 140
ys, xs = np.nonzero(m)
print('файл', im.size, 'маска: x %d..%d, y %d..%d' % (xs.min(), xs.max(), ys.min(), ys.max()))

# PCA главной оси
X = np.stack([xs - xs.mean(), ys - ys.mean()], axis=1).astype(np.float64)
C = X.T @ X / len(X)
w, v = np.linalg.eigh(C)
main = v[:, np.argmax(w)]
ang = np.degrees(np.arctan2(-main[1], main[0]))   # экранные y вниз -> минус
print('главная ось: %.1f° к горизонтали (плюс = вверх-вправо), отношение осей %.2f'
      % (ang, np.sqrt(w.max() / w.min())))

# «верхняя кромка» маски по колонкам: как меняется высота скамейки вдоль длины
h_cols = []
for x in range(xs.min(), xs.max() + 1, 40):
    col = np.nonzero(m[:, x])[0]
    if len(col):
        h_cols.append((x, col.min(), col.max()))
print('\nколонка -> верх/низ маски (px в файле):')
for x, t, b in h_cols:
    print('  x=%4d  верх %3d  низ %3d  высота %3d' % (x, t, b, b - t))
