# -*- coding: utf-8 -*-
"""Проверка каймы уже в СОБРАННОМ кадре: яркость пикселей по контуру поэта."""
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, '_sat')

with open(os.path.join(OUT, 'final_params.json')) as f:
    P = json.load(f)
H, W = P['h_px'], P['top']
LEFT = P['left']


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


def measure(frame, sprite):
    sp = Image.open(os.path.join(ROOT, 'vn2', 'img', 'char', sprite)).convert('RGBA')
    sp = sp.resize((max(1, round(sp.width * H / sp.height)), H), Image.LANCZOS)
    al = np.asarray(sp)[:, :, 3] > 200
    mask = np.zeros((1080, 1920), bool)
    w = sp.width
    mask[P['top']:P['top'] + H, LEFT:LEFT + w] = al
    edge = mask & ~erode(mask, 2)
    img = np.asarray(Image.open(os.path.join(OUT, frame)).convert('RGB')).astype(float)
    lum = 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
    core = lum[erode(mask, 6)].mean()
    e = lum[edge]
    return core, e.mean(), np.percentile(e, 90), (e > core + 25).sum(), e.size


for frame, sprite, lab in (('EDGE_before_full.jpg', 'poet_seat_upset.webp', 'было'),
                           ('EDGE_after_full.jpg', 'poet_seat_upset_fixed.webp', 'стало')):
    core, em, p90, nlight, n = measure(frame, sprite)
    print('%s: ядро %.1f, кромка ср %.1f, 90%% %.1f, светлее ядра на 25+ : %d из %d (%.1f%%)'
          % (lab, core, em, p90, nlight, n, 100.0 * nlight / max(1, n)))
