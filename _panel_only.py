# -*- coding: utf-8 -*-
"""Крупный кроп ТОЛЬКО панели (без слоя) — есть ли в кадре нарисованные буквы."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, '_sat', 'demo_s5a_no_ovl.png')
im = Image.open(p).convert('RGB')
W, H = im.size
k = W / 2400.0
box = (int(1119 * k), int(505 * k), int(1848 * k), int(890 * k))
c = im.crop(box)
c = c.resize((c.size[0] * 4, c.size[1] * 4), Image.LANCZOS)
o = os.path.join(HERE, '_sat', 'panel_only.png')
c.save(o)
print('crop', box, '->', c.size)

# и та же панель в финальном PNG (2400-пространство, без слоя движка)
f = Image.open(os.path.join(HERE, 'assets', 'final', 'prolog', 's5a.png')).convert('RGB')
k2 = f.size[0] / 2400.0
c2 = f.crop((int(1119 * k2), int(505 * k2), int(1848 * k2), int(890 * k2)))
c2 = c2.resize((c2.size[0] * 2, c2.size[1] * 2), Image.LANCZOS)
o2 = os.path.join(HERE, '_sat', 'panel_final.png')
c2.save(o2)
print('final crop ->', c2.size)
