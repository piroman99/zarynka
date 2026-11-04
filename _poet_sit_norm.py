# -*- coding: utf-8 -*-
"""Сидящий поэт: матирование + нормировка трёх эмоций между собой (0 ₽).

Сидящая фигура обрезана по колено, поэтому к стоячему касту (плечи/холст 0.56) её
приводить нельзя — она законно «шире». Нормируем ДРУГ К ДРУГУ: плечи/высота холста
= 0.60, низ фигуры на нижней кромке (сидит на уровне скамейки).
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
TARGET_SH = 0.60
SIDE = 0.03


def shoulders(mask):
    ys, xs = np.nonzero(mask)
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0
    band = mask[y0 + int(bh * 0.30):y0 + int(bh * 0.55)]
    cols = np.nonzero(band.any(0))[0]
    return (int(cols.max() - cols.min()) if len(cols) else 0), bh


for key in ('upset', 'neutral', 'interested'):
    src = os.path.join(GEN, 'sit_%s_0.png' % key)
    if not os.path.exists(src):
        print('нет', src)
        continue
    rgba, st = matte(Image.open(src))
    m = np.asarray(rgba.split()[-1]) > 128
    sh, _bh = shoulders(m)
    canvas_h = int(round(sh / TARGET_SH))
    ys, xs = np.nonzero(m)
    fig = rgba.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    mw = int(round(fig.width * SIDE))
    canvas = Image.new('RGBA', (fig.width + 2 * mw, canvas_h), (0, 0, 0, 0))
    if canvas_h >= fig.height:
        canvas.alpha_composite(fig, (mw, canvas_h - fig.height))
    else:
        canvas.alpha_composite(fig.crop((0, 0, fig.width, canvas_h)), (mw, 0))
    out = os.path.join(SPR, 'poet_sit_%s.png' % key)
    canvas.save(out)
    m2 = np.asarray(canvas.split()[-1]) > 128
    sh2, _ = shoulders(m2)
    print('%-10s %4dx%-4d -> %dx%d  плечи %.3f  фон снят %.0f%%'
          % (key, Image.open(src).width, Image.open(src).height,
             canvas.width, canvas.height, sh2 / canvas.height, 100 * st['removed']))
