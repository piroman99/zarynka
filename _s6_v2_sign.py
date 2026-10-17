# -*- coding: utf-8 -*-
"""Кроп вывески v2 в нативном разрешении (проверка букв)."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
for tag, rel, box in (
    ('a', 'assets/gen/s6_gpt2_a_0.png', (0.10, 0.02, 0.95, 0.19)),
    ('b', 'assets/gen/s6_gpt2_b_0.png', (0.08, 0.02, 0.98, 0.18)),
):
    im = Image.open(os.path.join(HERE, rel)).convert('RGB')
    w, h = im.size
    c = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
    c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
    p = os.path.join(HERE, 'assets', 'review', '_s6_v2_sign_%s.png' % tag)
    c.save(p)
    print(p, c.size)
