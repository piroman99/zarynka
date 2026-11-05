# -*- coding: utf-8 -*-
"""Матирование новых ассетов правки (скамейка-проп + сидящий поэт без скамейки).

Печатает силуэт (ASCII) и метрики, по которым я выставляю геометрию без глаз:
  • скамейка: доли высоты кадра — верх спинки, линия сиденья (по просвету под сиденьем),
    низ ножек;
  • поэт: bbox, линия бёдер (низ фигуры).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _poet_matte import matte  # noqa: E402

GEN = os.path.join(HERE, 'assets', 'gen')
SPR = os.path.join(HERE, 'assets', 'sprites')
OUT = os.path.join(HERE, 'assets', 'staging')
os.makedirs(OUT, exist_ok=True)
os.makedirs(SPR, exist_ok=True)


def ascii_mask(mask, cols=64, title=''):
    rows = max(1, int(round(cols * mask.shape[0] / mask.shape[1] * 0.5)))
    h, w = mask.shape
    ch, cw = h / rows, w / cols
    print(title)
    print('    ' + ''.join(str((i // 10) % 10) for i in range(cols)))
    for ry in range(rows):
        line = ''
        for rx in range(cols):
            v = mask[int(ry * ch):int((ry + 1) * ch), int(rx * cw):int((rx + 1) * cw)].mean()
            line += '#' if v > .55 else ('+' if v > .18 else '.')
        print('%3d %s' % (ry, line))
    return rows


def band_rows(mask):
    """Доля заполнения по строкам — чтобы найти просвет под сиденьем и линию сиденья."""
    prof = mask.mean(1)
    return prof


for name in sys.argv[1:]:
    src = os.path.join(GEN, name + '_0.png')
    if not os.path.exists(src):
        print('нет', src)
        continue
    rgba, st = matte(Image.open(src))
    a = np.asarray(rgba.split()[-1])
    mask = a > 96
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    print('\n== %s  %dx%d  bbox x %d..%d y %d..%d  (фигура %.0f%% высоты, %.0f%% ширины)'
          % (name, rgba.width, rgba.height, x0, x1, y0, y1,
             100 * (y1 - y0) / rgba.height, 100 * (x1 - x0) / rgba.width))
    print('   фон снят %.0f%%, полупрозрачных %.1f%%'
          % (100 * st['removed'], 100 * float(((a > 8) & (a < 246)).mean())))
    ascii_mask(mask[:, x0:x1 + 1], cols=52, title='   силуэт:')
    # профиль ширины по 20 строкам bbox
    fig = mask[y0:y1 + 1, x0:x1 + 1]
    h = fig.shape[0]
    print('   профиль (доля высоты фигуры -> ширина в %% ширины фигуры):')
    for k in range(21):
        yy = min(h - 1, int(k / 20 * (h - 1)))
        c = np.nonzero(fig[yy])[0]
        print('     %3d%%  ширина %3.0f%%  (%d..%d)'
              % (100 * k / 20, 100 * (c.max() - c.min()) / fig.shape[1] if len(c) else 0,
                 c.min() if len(c) else -1, c.max() if len(c) else -1))
    dst = os.path.join(OUT, name + '_matte.png')
    rgba.save(dst)
    print('   -> %s' % os.path.relpath(dst, HERE))
