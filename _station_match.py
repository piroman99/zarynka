# -*- coding: utf-8 -*-
"""Какой кадр тизера соответствует арту станции + оценка «резкость на 1920».

Сравниваем кадры с артом по превью 64x36 (косинус), плюс считаем локальный контраст
(градиент) на одинаковом масштабе 1920 — так видно, где настоящие 1080p, а где апскейл.
"""
import glob
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '.tmp_vo', 'avm')


def vec(im, size=(64, 36)):
    a = np.asarray(im.convert('L').resize(size, Image.LANCZOS)).astype(np.float32)
    a = (a - a.mean()) / (a.std() + 1e-6)
    return a.reshape(-1)


def grad(im):
    a = np.asarray(im.convert('L').resize((1920, 1080), Image.LANCZOS)).astype(np.float32)
    gx = np.abs(np.diff(a, axis=1)).mean()
    gy = np.abs(np.diff(a, axis=0)).mean()
    return (gx + gy) / 2.0


art = Image.open(os.path.join(HERE, 'assets/gen/ok_space_station_0.jpg')).convert('RGB')
v_art = vec(art)
print('арт станции: градиент на 1920 = %.2f (нативное 1344x768)' % grad(art))

best = []
for p in sorted(glob.glob(os.path.join(OUT, 'f_*.png'))):
    im = Image.open(p)
    c = float(np.dot(vec(im), v_art) / len(v_art))
    best.append((c, os.path.basename(p), grad(im)))
best.sort(reverse=True)
print('\nблизость к арту станции (1.0 = тот же кадр):')
for c, n, g in best[:8]:
    print('  %-11s %.3f   градиент %.2f' % (n, c, g))
print('\nсамые «чистые» по градиенту кадры:')
for c, n, g in sorted(best, key=lambda r: -r[2])[:6]:
    print('  %-11s градиент %.2f   близость %.3f' % (n, g, c))
