# -*- coding: utf-8 -*-
"""Меряет bbox персонажа в каждой эмоции поэта: одинаковая ли крупность кадра.

Движок ставит спрайт фиксированной высотой, поэтому если у одной эмоции фигура
занимает 80 % кадра, а у другой 60 %, при переключении «прыгает» голова.
Норма — bbox_h / H в пределах ±3 %.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')

NAMES = ['poet2_b_0.png', 'poet_ha_neutral', 'poet_ha_interested', 'poet_ha_upset',
         'poet_sh_neutral', 'poet_sh_tired', 'poet_sh_inspired']


def f(name):
    if name.endswith('.png'):
        return os.path.join(GEN, name)
    for ext in ('.png', '.jpg'):
        p = os.path.join(GEN, name + '_0' + ext)
        if os.path.exists(p):
            return p
    return None


for n in NAMES:
    p = f(n)
    a = np.asarray(Image.open(p).convert('RGB'), np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    mask = np.abs(a - bg).max(2) > 26
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    bh, bw = y1 - y0, x1 - x0
    # голова: верхние 30 % bbox — ширина головы даёт масштаб лица
    head = mask[y0:y0 + int(bh * 0.30)]
    hx = np.nonzero(head.any(0))[0]
    head_w = (hx.max() - hx.min()) if len(hx) else 0
    print('%-22s %4dx%-4d bbox %dx%-4d  h/H %.3f  w/W %.3f  голова/ширина %.3f  aspect %.2f'
          % (n, w, h, bw, bh, bh / h, bw / w, head_w / w, bw / bh))
