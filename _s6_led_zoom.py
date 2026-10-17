# -*- coding: utf-8 -*-
"""Кроп C1/C2 в нативном разрешении: проверить, что цифры читаются как 06:07."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
import _s6_clock_ab as C

src = os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')
im = Image.open(src).convert('RGB').resize((2400, 1350), Image.LANCZOS)
for tag, box in (('c1', (1898, 322, 2108, 412)), ('c2', (1428, 430, 1600, 512))):
    v = C.clock(im.copy(), box)
    c = v.crop((box[0] - 90, box[1] - 70, box[2] + 90, box[3] + 70))
    c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS)
    p = os.path.join(HERE, 'assets', 'review', '_s6_led_%s.png' % tag)
    c.save(p)
    print(p, c.size)
