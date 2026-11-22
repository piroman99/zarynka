# -*- coding: utf-8 -*-
"""Замер: где на самом деле непрозрачная часть пропа bench.webp и спрайтов поэта/Кate."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
for p in ['vn2/img/prop/bench.webp', 'vn2/img/char/poet_seat_upset.webp',
          'vn2/img/char/kate.webp', 'assets/gen/alley_b_nobench__gpt-image-2_0.png']:
    f = os.path.join(HERE, p)
    im = Image.open(f)
    print(p, im.size, im.mode, end=' ')
    if im.mode in ('RGBA', 'LA'):
        a = im.getchannel('A')
        bb = a.getbbox()
        print('alpha bbox', bb, 'w x h =', (bb[2] - bb[0], bb[3] - bb[1]) if bb else None)
    else:
        print('(нет альфы)')
