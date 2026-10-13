# -*- coding: utf-8 -*-
"""Уменьшенный превью S4-финала + сетка координат, чтобы выбрать точку наезда (Марс)."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, 'assets', 'final', 'prolog', 's4.png')).convert('RGB')
W, H = 480, 270
sm = im.resize((W, H), Image.LANCZOS)
d = ImageDraw.Draw(sm)
for fx in (0.25, 0.5, 0.75):
    d.line([(W * fx, 0), (W * fx, H)], fill=(0, 255, 0), width=1)
for fy in (0.25, 0.5, 0.75):
    d.line([(0, H * fy), (W, H * fy)], fill=(0, 255, 0), width=1)
sm.save(os.path.join(HERE, '_tmp_s4_preview.jpg'), quality=88)
print('ok', os.path.join('novella/zaryanka/_tmp_s4_preview.jpg'))
