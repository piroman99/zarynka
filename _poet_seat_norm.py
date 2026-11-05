# -*- coding: utf-8 -*-
"""Сидящие спрайты поэта (6 эмоций) — маттинг + нормировка по ГОЛОВЕ.

Почему по голове (а не по плечам, как у стоячего каста): позы разные (сгорбился,
закрыл лицо, поднял плечи), и плечи «гуляют» на ±28 %. Голова же одна и та же —
её ширина и есть масштаб кадра.

Геометрия:
  • head/canvas_h = 0.16  → при `height:75%` на сцене голова 108 px у всех эмоций;
    это сверено с Екатериной (749 px на 1.70 м ≈ 440 px/м, голова с волосами ≈ 0.24 м);
  • низ фигуры (ступни) = низ холста + 1 % → линия бёдер/сиденья всегда на
    30 % высоты холста (0.45 м посадки при 450 px/м) — сидит на скамейке ровно.

Выход: assets/sprites/poet_seat_<emo>.png
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
os.makedirs(SPR, exist_ok=True)

HEAD_SH = 0.16        # ширина головы / высота холста
HIP_FRAC = 0.30       # линия сиденья от низа холста (0.45 м / 0.24 м × 0.16)
BOTTOM = 0.01         # поля снизу, доля высоты холста
SIDE = 0.04

FILES = [('neutral', 'sit2_neutral'), ('upset', 'sit_upset'), ('interested', 'sit_interested'),
         ('shy', 'sit_shy'), ('sullen', 'sit_sullen'), ('smile', 'sit_smile')]


def head_width(mask):
    ys, _xs = np.nonzero(mask)
    y0, y1 = ys.min(), ys.max()
    bh = y1 - y0
    band = mask[y0:y0 + max(2, int(bh * 0.12))]
    cols = np.nonzero(band.any(0))[0]
    return int(cols.max() - cols.min())


for em, stem in FILES:
    src = os.path.join(GEN, stem + '_0.png')
    if not os.path.exists(src):
        print('нет', src)
        continue
    rgba, st = matte(Image.open(src))
    m = np.asarray(rgba.split()[-1]) > 128
    hd = head_width(m)
    if not hd:
        print('%-10s голова не найдена' % em)
        continue
    canvas_h = int(round(hd / HEAD_SH))
    ys, xs = np.nonzero(m)
    fig = rgba.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    side = int(round(fig.width * SIDE))
    canvas_w = fig.width + 2 * side
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    bottom_pad = max(0, int(round(canvas_h * BOTTOM)))
    top = canvas_h - bottom_pad - fig.height
    if top < 0:                       # фигура выше холста — подрезаем сверху, не низ
        fig = fig.crop((0, -top, fig.width, fig.height))
        top = 0
    canvas.alpha_composite(fig, (side, top))
    out = os.path.join(SPR, 'poet_seat_%s.png' % em)
    canvas.save(out)
    print('%-10s голова %3d -> холст %dx%-4d  фигура %dx%d  сиденье y=%+d (%.0f%% холста)  '
          'фон снят %.0f%%  -> %s'
          % (em, hd, canvas_w, canvas_h, fig.width, fig.height,
             -int(round(canvas_h * HIP_FRAC)), 100 * HIP_FRAC,
             100 * st['removed'], os.path.relpath(out, HERE)))