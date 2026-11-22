# -*- coding: utf-8 -*-
"""Размеры исходников: фон аллеи, проп-скамейка, сидячий поэт."""
import os
import glob
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
files = [
    'assets/gen/alley_b_0.jpg',
    'assets/gen/bench_long_0.png',
    'vn2/img/bg/alley.webp',
    'vn2/img/prop/bench.webp',
] + sorted(glob.glob(os.path.join(ROOT, 'assets', 'sprites', 'poet_sit*.png'))) \
  + sorted(glob.glob(os.path.join(ROOT, 'assets', 'sprites', 'poet_seat*.png'))) \
  + sorted(glob.glob(os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat*.webp')))

for f in files:
    p = f if os.path.isabs(f) else os.path.join(HERE, f)
    if not os.path.exists(p):
        print('НЕТ  ', f)
        continue
    im = Image.open(p)
    print('%-58s %s %s %d B' % (os.path.relpath(p, HERE), im.mode,
                                '%dx%d' % im.size, os.path.getsize(p)))
