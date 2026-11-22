# -*- coding: utf-8 -*-
"""Уборка временных превью/скриншотов наезда S4."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
gone = [
    os.path.join(HERE, '_tmp_s4_preview.jpg'),
    os.path.join(ROOT, 'assets', 'review', '_tmp_s4_beat1.png'),
    os.path.join(ROOT, 'assets', 'review', '_tmp_s4_beat2.png'),
    os.path.join(ROOT, 'assets', 'review', '_tmp_engine_b1.png'),
    os.path.join(ROOT, 'assets', 'review', '_tmp_engine_b2.png'),
]
for p in gone:
    if os.path.exists(p):
        os.remove(p)
        print('del', os.path.relpath(p, HERE))
print('уборка ок')
