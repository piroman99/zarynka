# -*- coding: utf-8 -*-
"""Быстрая проверка: вырезать кропы пасхалок крупно для визуального контроля."""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _prolog_eggs as E   # noqa
T = os.path.join(HERE, '.tmp_diag')
os.makedirs(T, exist_ok=True)
names = ['s1_katobus', 's2_bus410', 's6_clock', 's6_plaque', 'p0_bird']
for (frame, box, cap), nm in zip(E.ROWS, names):
    c = frame.crop(box)
    sc = min(1100 / c.width, 760 / c.height)
    c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
    p = os.path.join(T, nm + '.png')
    c.save(p)
    print(nm, c.size, os.path.relpath(p, HERE))
