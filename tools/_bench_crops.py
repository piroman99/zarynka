# -*- coding: utf-8 -*-
"""Кропы: скамейка в кадре целиком и крупно (чтобы видеть винты)."""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
PREFIX = sys.argv[1] if len(sys.argv) > 1 else 'blend8'
FULL = os.path.join(ROOT, '_sat', PREFIX + '_full.jpg')
OUTDIR = os.path.join(ROOT, '_sat')

im = Image.open(FULL).convert('RGB')

c1 = im.crop((60, 400, 800, 1000))
c1.save(os.path.join(OUTDIR, PREFIX + '_bench.jpg'), quality=93)

c2 = im.crop((150, 560, 640, 900))
c2 = c2.resize((int(c2.width * 2.0), int(c2.height * 2.0)), Image.LANCZOS)
c2.save(os.path.join(OUTDIR, PREFIX + '_bench_zoom.jpg'), quality=94)

print('saved', PREFIX + '_bench.jpg', c1.size, os.path.getsize(os.path.join(OUTDIR, PREFIX + '_bench.jpg')))
print('saved', PREFIX + '_bench_zoom.jpg', c2.size, os.path.getsize(os.path.join(OUTDIR, PREFIX + '_bench_zoom.jpg')))
