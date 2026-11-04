# -*- coding: utf-8 -*-
"""Мелкие кропы «проблемных зон» из снимков кадров — по одному файлу, чтобы прочитать."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, '_sat', '_all')
OUT = os.path.join(HERE, '_sat')

# (узел, страница, box в 2400x1350) — верхний левый угол с меткой сцены + оверлей
JOBS = [('s3', 0, (0, 0, 2400, 1350)), ('s4', 0, (0, 0, 2400, 1350)),
        ('s5a', 0, (0, 0, 2400, 1350)), ('s5b', 0, (0, 0, 2400, 1350))]
for name, page, box in JOBS:
    im = Image.open(os.path.join(T, '%s_%d.png' % (name, page))).convert('RGB')
    W, H = im.size
    k = W / 2400.0
    b = tuple(int(v * k) for v in box)
    c = im.crop(b)
    c = c.resize((int(c.size[0] * 0.42), int(c.size[1] * 0.42)), Image.LANCZOS)
    p = os.path.join(OUT, 'chk_%s.png' % name)
    c.save(p)
    print(os.path.relpath(p, HERE), c.size)
