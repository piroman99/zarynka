# -*- coding: utf-8 -*-
"""Сравнение двух семейств поз: poet_seat_* и poet_sit_*.

Для посадки на скамейку нужно: таз (место, где силуэт перестаёт быть цельным
поперёк) как можно ближе к низу файла, а ноги — отдельными узкими колонками.
Печатаем bbox, долю таза, долю низа и ширину «ног» внизу.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')


def runs_of(row, min_len=8):
    out, s = [], None
    w = len(row)
    for x in range(w + 1):
        v = row[x] if x < w else False
        if v and s is None:
            s = x
        elif not v and s is not None:
            if x - s >= min_len:
                out.append((s, x - 1))
            s = None
    return out


def analyse(path):
    im = Image.open(path).convert('RGBA')
    a = np.asarray(im)[:, :, 3] > 100
    h, w = a.shape
    rows = np.nonzero(a.any(axis=1))[0]
    f_top, f_bot = rows.min() / h, rows.max() / h

    two = []
    for y in range(int(h * 0.99), int(h * 0.40), -1):
        if len(runs_of(a[y])) >= 2:
            two.append(y)
        elif two:
            break
    f_seat = (two[-1] + 1) / h if two else None
    f_split_low = two[0] / h if two else None

    # ширина ног внизу
    leg_rows = [y for y in range(int(h * 0.90), int(h * 0.99)) if runs_of(a[y])]
    widths = [sum(e - s + 1 for s, e in runs_of(a[y])) for y in leg_rows]
    n_legs = [len(runs_of(a[y])) for y in leg_rows]

    print('%-28s %4dx%-4d верх %.3f низ %.3f таз %.3f  ног внизу %.1f  ширина %.0f%% файла'
          % (os.path.basename(path), w, h, f_top, f_bot,
             f_seat if f_seat else -1, np.mean(n_legs) if n_legs else 0,
             100.0 * np.mean(widths) / w if widths else 0))
    return f_top, f_bot, f_seat


for name in ('poet_seat_upset.webp', 'poet_sit_upset.webp', 'poet_seat.webp', 'poet_sit.webp',
             'poet_seat_shy.webp', 'poet.webp', 'poet_sit_interested.webp'):
    p = os.path.join(CHAR, name)
    if os.path.exists(p):
        analyse(p)
