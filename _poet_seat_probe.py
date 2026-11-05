# -*- coding: utf-8 -*-
"""Какая мерка у сидящих кадров стабильна между эмоциями: голова или плечи?

Печатает по каждому кадру: bbox, ширину головы (верхние 12 % bbox), ширину «плеч»
в разных поясах, ширину бёдер (60–70 %). По разбросу видно, на что нормировать.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _poet_matte import matte  # noqa: E402

GEN = os.path.join(HERE, 'assets', 'gen')
EMOS = ['neutral', 'upset', 'interested', 'shy', 'sullen', 'smile']

def span(mask, y0, y1):
    band = mask[y0:y1]
    c = np.nonzero(band.any(0))[0]
    return int(c.max() - c.min()) if len(c) else 0

rows = []
for em in EMOS:
    src = os.path.join(GEN, 'sit_%s_0.png' % em)
    if not os.path.exists(src):
        continue
    rgba, _st = matte(Image.open(src))
    m = np.asarray(rgba.split()[-1]) > 128
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    f = m[y0:y1 + 1, x0:x1 + 1]
    h, w = f.shape
    head = span(f, 0, max(2, int(h * 0.12)))
    sh22 = span(f, int(h * 0.22), int(h * 0.40))
    sh35 = span(f, int(h * 0.35), int(h * 0.55))
    hip = span(f, int(h * 0.60), int(h * 0.70))
    rows.append((em, w, h, head, sh22, sh35, hip))
    print('%-11s bbox %4dx%-4d  голова %3d (%.3f)  плечи22-40 %3d (%.3f)  '
          'плечи35-55 %3d (%.3f)  бёдра %3d (%.3f)'
          % (em, w, h, head, head / h, sh22, sh22 / h, sh35, sh35 / h, hip, hip / h))

for i, name in ((3, 'голова'), (4, 'плечи22-40'), (5, 'плечи35-55'), (6, 'бёдра')):
    v = np.array([r[i] for r in rows], np.float32)
    print('%-12s разброс по эмоциям: min %d max %d  (%+.0f%% .. %+.0f%% от медианы)'
          % (name, v.min(), v.max(), 100 * (v.min() / np.median(v) - 1),
             100 * (v.max() / np.median(v) - 1)))
