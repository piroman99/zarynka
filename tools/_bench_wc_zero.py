# -*- coding: utf-8 -*-
"""Сохранить «нулевой» проп (без обработки) в конечном масштабе — для сравнения."""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
src = Image.open(os.path.join(ROOT, '_sat', 'blend', 'bench8.png')).convert('RGBA')
w = 876
h = max(1, round(src.height * (w / float(src.width))))
out = src.resize((w, h), Image.LANCZOS)
p = os.path.join(ROOT, '_sat', 'wc', 'prop_0.png')
out.save(p)
print('saved', os.path.relpath(p, HERE), out.size, os.path.getsize(p), 'B')
