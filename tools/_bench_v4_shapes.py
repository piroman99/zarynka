# -*- coding: utf-8 -*-
"""Сравнение силуэтов v2 (fixed2) и v4: профили, поиск ножек, перенос опорных точек."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P2 = os.path.join(ROOT, '_sat', 'prop_bench_new_fixed2.png')
P4 = os.path.join(ROOT, '_sat', 'prop_bench_v4_matte.png')


def load(p):
    im = Image.open(p).convert('RGBA')
    a = np.asarray(im)[:, :, 3]
    return im, (a > 140)


def cols_prof(m, step=2):
    h, w = m.shape
    out = []
    for c in range(0, 100, step):
        x0 = int(w * c / 100.0)
        x1 = max(int(w * (c + step) / 100.0), x0 + 1)
        col = m[:, x0:x1].any(axis=1)
        idx = np.nonzero(col)[0]
        out.append((c, x0, int(idx.min()) if idx.size else -1,
                    int(idx.max()) if idx.size else -1))
    return out


def feet(m, k=7):
    """низ маски по каждой колонке, сглаженный, ищем локальные максимумы низа (опоры)."""
    h, w = m.shape
    bot = np.full(w, -1.0)
    for x in range(w):
        idx = np.nonzero(m[:, x])[0]
        if idx.size:
            bot[x] = idx.max()
    filled = bot.copy()
    ok = filled >= 0
    xs = np.arange(w)
    filled[~ok] = np.interp(xs[~ok], xs[ok], filled[ok])
    kk = np.ones(2 * k + 1) / (2 * k + 1)
    sm = np.convolve(filled, kk, mode='same')
    peaks = []
    for x in range(k + 5, w - k - 5):
        if sm[x] == sm[max(0, x - 12):x + 13].max() and sm[x] > sm[x - 12] + 1.0:
            if not peaks or x - peaks[-1][0] > 30:
                peaks.append((x, float(sm[x])))
            elif sm[x] > peaks[-1][1]:
                peaks[-1] = (x, float(sm[x]))
    return bot, sm, peaks


for name, p in (('v2', P2), ('v4', P4)):
    im, m = load(p)
    h, w = m.shape
    bot, sm, peaks = feet(m)
    print('=== %s %dx%d  fill %.1f%%' % (name, w, h, 100.0 * m.mean()))
    print('  опоры (x, низ) в пикселях: %s' % [(int(x), round(y)) for x, y in peaks])
    print('  опоры в долях: %s' % [('%.3f' % (x / w), '%.3f' % (y / h)) for x, y in peaks])
    prof = cols_prof(m, 4)
    print('  профиль 4%: ' + ' '.join('%d:%d-%d' % (c, t, b) for c, x, t, b in prof))
    print()
