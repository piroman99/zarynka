# -*- coding: utf-8 -*-
"""1) Крупный кроп чипа кадра 12 (s5b) из живого демо. 2) Есть ли глифы в woff2-сабсетах."""
import os
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '_pylib'))
from fontTools.ttLib import TTFont  # noqa: E402

# --- 1. кроп чипа
im = Image.open(os.path.join(HERE, '_sat', 'demo_s5b.png')).convert('RGB')
W, H = im.size
k = W / 2400.0
box = (int(520 * k), int(800 * k), int(1400 * k), int(950 * k))
c = im.crop(box)
c = c.resize((c.size[0] * 4, c.size[1] * 4), Image.LANCZOS)
o = os.path.join(HERE, '_sat', 's5b_chip_zoom.png')
c.save(o)
print('кроп чипа ->', os.path.relpath(o, HERE), c.size)

# --- 2. глифы
FONTS = os.path.join(HERE, 'vn2', 'fonts')
print('шрифты:', sorted(f for f in os.listdir(FONTS) if f.endswith('.woff2')))
NEED = set('Ёё—«»!?·ДВАМЕСТЛЮИЦЫМАРСДЕЛОБЩ!')
for fn in sorted(f for f in os.listdir(FONTS) if f.endswith('.woff2')):
    f = TTFont(os.path.join(FONTS, fn))
    cmap = set()
    for t in f['cmap'].tables:
        cmap |= set(t.cmap.keys())
    miss = sorted(ch for ch in NEED if ord(ch) not in cmap)
    print('%-18s глифов=%4d  нет: %s' % (fn, len(cmap),
                                         ''.join(miss) if miss else '—'))
