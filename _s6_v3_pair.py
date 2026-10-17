# -*- coding: utf-8 -*-
"""Кроп пары в нативном разрешении — проверить очки, книгу, руку (пасхалка читается?)."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for tag, rel, box in (
    ('a', 'assets/gen/s6_gpt3_a_0.png', (0.24, 0.34, 0.66, 0.98)),
    ('b', 'assets/gen/s6_gpt3_b_0.png', (0.04, 0.22, 0.50, 1.0)),
):
    im = Image.open(os.path.join(HERE, rel)).convert('RGB')
    w, h = im.size
    c = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    p = os.path.join(HERE, 'assets', 'review', '_s6_v3_pair_%s.png' % tag)
    c.save(p)
    print(p, c.size)
