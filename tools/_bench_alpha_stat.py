# -*- coding: utf-8 -*-
"""Числовая проверка: стало ли плотным правое крыло скамейки (до/после усиления)."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SPR = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')


def stat(arr, x0f, x1f):
    Wf = arr.shape[1]
    sub = arr[:, int(Wf * x0f):int(Wf * x1f), 3]
    return (100.0 * (sub > 200).mean(), 100.0 * (sub > 140).mean(), float(sub.mean()))


base = np.asarray(Image.open(SPR).convert('RGBA')).astype(np.float32)
print('%-14s %s' % ('полоса файла', 'плотных>200 / видимых>140 / средняя альфа'))
for name, a in [('исходник', base)]:
    for x0, x1 in ((0.0, 0.25), (0.4, 0.6), (0.6, 0.75), (0.75, 0.85), (0.85, 0.95)):
        d, v, mean = stat(a, x0, x1)
        print('%s x %.2f-%.2f: %5.1f%% %5.1f%% %6.1f' % (name, x0, x1, d, v, mean))

# после усиления — как в v3 (гамма 0.33 от 0.68)
alpha = base[:, :, 3]
Wf = alpha.shape[1]
xs = np.arange(Wf, dtype=np.float32) / Wf
w = np.clip((xs - 0.68) / 0.10, 0, 1)
w = w * w * (3 - 2 * w)
new = alpha + (255.0 * np.power(alpha / 255.0, 0.33) - alpha) * w[None, :]
fixed = base.copy()
fixed[:, :, 3] = np.clip(new, 0, 255)
print()
for x0, x1 in ((0.6, 0.75), (0.75, 0.85), (0.85, 0.95)):
    d, v, mean = stat(fixed, x0, x1)
    print('после  x %.2f-%.2f: %5.1f%% %5.1f%% %6.1f' % (x0, x1, d, v, mean))
p = os.path.join(ROOT, '_sat', 'prop_bench_v3.png')
Image.fromarray(fixed.astype(np.uint8), 'RGBA').save(p)
print('saved', os.path.relpath(p, HERE), os.path.getsize(p), 'B')
