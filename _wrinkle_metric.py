# -*- coding: utf-8 -*-
"""Число горизонтальных морщин на лбу и «текстурность» щетины.
Морщины: профиль яркости по строкам -> локальные минимумы с заметной глубиной.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 'assets', 'gen')
V2 = os.path.join(GEN, '_sergey_v2')

FILES = [
    ('base', os.path.join(GEN, 'sergey_eng_old__flux-2_0.jpg')),
    ('smile OLD', os.path.join(GEN, 'sergey_smile_0.jpg')),
    ('smile flux v2', os.path.join(V2, 'sergey_smile__flux-2_0.jpg')),
    ('smile gpt v2', os.path.join(V2, 'sergey_smile__gpt-image-2_0.png')),
    ('conc OLD', os.path.join(GEN, 'sergey_concerned_0.jpg')),
    ('conc flux v2', os.path.join(V2, 'sergey_concerned__flux-2_0.jpg')),
    ('conc gpt v2', os.path.join(V2, 'sergey_concerned__gpt-image-2_0.png')),
]
FORE = (.36, .62, .115, .215)
MUST = (.38, .64, .285, .355)


def wrinkle_lines(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im, np.float32)
    h, w = a.shape
    x0, x1, y0, y1 = FORE
    z = a[int(h * y0):int(h * y1), int(w * x0):int(w * x1)]
    prof = z.mean(1)
    prof = prof - np.convolve(prof, np.ones(11) / 11, 'same')   # убрать общий градиент
    lines = 0
    depth = 0.0
    for i in range(2, len(prof) - 2):
        if prof[i] < prof[i - 1] and prof[i] <= prof[i + 1]:
            prom = min(prof[i - 2] - prof[i], prof[i + 2] - prof[i])
            if prom > 1.5:
                lines += 1
                depth += prom
    return lines, depth


def stubble(path):
    im = Image.open(path).convert('L')
    a = np.asarray(im, np.float32)
    h, w = a.shape
    x0, x1, y0, y1 = MUST
    z = a[int(h * y0):int(h * y1), int(w * x0):int(w * x1)]
    lap = np.abs(4 * z[1:-1, 1:-1] - z[:-2, 1:-1] - z[2:, 1:-1] - z[1:-1, :-2] - z[1:-1, 2:])
    return lap.mean()


print('%-15s %7s %8s %9s' % ('', 'морщин', 'глубина', 'щетина'))
for label, p in FILES:
    n, dp = wrinkle_lines(p)
    print('%-15s %7d %8.1f %9.2f' % (label, n, dp, stubble(p)))
