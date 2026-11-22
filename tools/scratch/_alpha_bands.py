# -*- coding: utf-8 -*-
"""Плотность альфы по полосам: старый проп vs новый (после матирования)."""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
for p, lab in [('_sat/prop_bench_new_matte.png', 'новый'),
               ('assets/sprites/prop_bench.png', 'старый')]:
    a = np.asarray(Image.open(os.path.join(HERE, p)).convert('RGBA'))
    Hf, Wf = a.shape[:2]
    print('%s %s %dx%d' % (lab, p, Wf, Hf))
    for i in range(8):
        x0, x1 = int(Wf * i / 8), int(Wf * (i + 1) / 8)
        s = a[:, x0:x1, 3]
        print('  x %.2f-%.2f: плотных>200 %5.1f%%  видимых>140 %5.1f%%  ср.альфа %6.1f'
              % (i / 8, (i + 1) / 8, 100 * (s > 200).mean(), 100 * (s > 140).mean(), s.mean()))
