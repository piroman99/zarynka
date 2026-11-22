# -*- coding: utf-8 -*-
"""Кроп кадра вокруг скамейки — чтобы видеть, как планки прибиты к стойкам."""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
FULL = os.path.join(ROOT, '_sat', 'blend2_full.jpg')
OUT = os.path.join(ROOT, '_sat', 'blend2_bench_zoom.jpg')

im = Image.open(FULL).convert('RGB')
c = im.crop((40, 380, 780, 1000))
c = c.resize((int(c.width * 1.7), int(c.height * 1.7)), Image.LANCZOS)
c.save(OUT, quality=93)
print('zoom', os.path.relpath(OUT, HERE), c.size, os.path.getsize(OUT), 'B')
