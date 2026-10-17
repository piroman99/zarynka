# -*- coding: utf-8 -*-
"""Кроп вывески в нативном разрешении — проверить буквы «ЗВЁЗДНЫЙ ГОРОДОК»."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for tag, rel, box in (
    ('a', 'assets/gen/s6_gpt_a_0.png', (0.10, 0.02, 0.90, 0.20)),
    ('b', 'assets/gen/s6_gpt_b_0.png', (0.10, 0.02, 0.95, 0.22)),
):
    im = Image.open(os.path.join(HERE, rel)).convert('RGB')
    w, h = im.size
    c = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    p = os.path.join(HERE, 'assets', 'review', '_s6_sign_%s.png' % tag)
    c.save(p)
    print(p, c.size)
