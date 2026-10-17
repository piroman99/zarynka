# -*- coding: utf-8 -*-
"""Очень крупный кроп вокруг табло C1 (4x) — честно посмотреть, как оно «сидит» на будке."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
import _s6_clock_ab as C

BOX = (1898, 322, 2108, 412)
plate = Image.open(os.path.join(HERE, 'assets', 'gen', 's6_gpt3_b_0.png')).convert('RGB')
plate = plate.resize((2400, 1350), Image.LANCZOS)
full = C.clock(plate.copy(), BOX)
c = full.crop((1780, 210, 2280, 520))
c = c.resize((c.width * 4, c.height * 4), Image.LANCZOS)
p = os.path.join(HERE, 'assets', 'review', '_s6_c1_tight.png')
c.save(p)
print(p, c.size)
