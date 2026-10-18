# -*- coding: utf-8 -*-
"""Где на кадре отличается от чистого фона: показывает, нарисован ли спрайт и где."""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '.tmp_vo')
BG = os.path.join(HERE, 'vn2', 'img', 'bg', 'reception.webp')

bg = Image.open(BG).convert('RGB')
for f in sorted(os.listdir(D)):
    if not f.startswith('shot_p'):
        continue
    im = Image.open(os.path.join(D, f)).convert('RGB')
    a = np.asarray(im, np.float32)
    h, w, _ = a.shape
    # фон вписан как cover в 16:9
    b = np.asarray(bg.resize((w, h), Image.LANCZOS), np.float32)
    d = np.abs(a - b).mean(2)
    mask = d > 40
    # сетка 6x4 — где отличия
    gh, gw = 4, 6
    print('==', f, 'diff=%.1f%%' % (100 * mask.mean()))
    for gy in range(gh):
        row = ''
        for gx in range(gw):
            cell = mask[gy * h // gh:(gy + 1) * h // gh, gx * w // gw:(gx + 1) * w // gw]
            row += '%4.0f' % (100 * cell.mean())
        print('   ', row)
