# -*- coding: utf-8 -*-
"""Один масштаб для всех шести сидящих спрайтов поэта (0 ₽, только паддинг).

ЗАМЕР `_seat_fill.py`: сейчас фигура занимает от 70 % (upset) до 88 % (interested)
высоты холста, а движок масштабирует ХОЛСТ. Значит при смене эмоции поэт «прыгает»
по размеру до 25 %, а линия бёдер гуляет 25.3…31.5 % холста — то есть он ещё и
садится на скамейку по-разному.

Здесь приводим всех к одному: высота фигуры = FILL высоты холста, ступни = BOTTOM
от низа холста. Тогда бёдра у всех на одной линии (0.346 высоты фигуры от ступней).

Выход перезаписывает assets/sprites/poet_seat_<emo>.png (холст только растёт).
"""
import os
import glob

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SPR = os.path.join(HERE, 'assets', 'sprites')
FILL = 0.85          # высота фигуры / высота холста
BOTTOM = 0.01        # ступни на 1 % холста выше низа
HIP = 0.346          # посадка / высота фигуры


def bbox(m):
    ys, xs = np.nonzero(m)
    return xs.min(), xs.max(), ys.min(), ys.max()


for p in sorted(glob.glob(os.path.join(SPR, 'poet_seat_*.png'))):
    im = Image.open(p).convert('RGBA')
    m = np.asarray(im.split()[-1]) > 128
    x0, x1, y0, y1 = bbox(m)
    fig = im.crop((x0, y0, x1 + 1, y1 + 1))
    canvas_h = int(round(fig.height / FILL))
    side = int(round(fig.width * 0.04))
    canvas = Image.new('RGBA', (fig.width + 2 * side, canvas_h), (0, 0, 0, 0))
    bottom_pad = int(round(canvas_h * BOTTOM))
    top = canvas_h - bottom_pad - fig.height
    assert top >= 0, 'фигура выше холста: %s' % p
    canvas.alpha_composite(fig, (side, top))
    canvas.save(p)
    m2 = np.asarray(canvas.split()[-1]) > 128
    _, _, y0b, y1b = bbox(m2)
    fh = y1b - y0b + 1
    print('%-26s фигура %4d px = %.3f холста, ступни %d px от низа, '
          'бёдра на %.1f%% холста, холст %dx%d'
          % (os.path.basename(p), fh, fh / canvas_h,
             canvas_h - 1 - y1b, 100.0 * (canvas_h - 1 - y1b + HIP * fh) / canvas_h,
             canvas.width, canvas_h))
