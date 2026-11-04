#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Уменьшенные копии текущих кадров s3/s4/s5 для просмотра (без букв в нативе)."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', 'final', 'prolog')
OUT = os.path.join(HERE, '_sat')
os.makedirs(OUT, exist_ok=True)

for n in ('s3', 's4', 's5'):
    im = Image.open(os.path.join(SRC, n + '.png')).convert('RGB')
    w, h = im.size
    nw = 880
    im2 = im.resize((nw, round(h * nw / w)), Image.LANCZOS)
    p = os.path.join(OUT, 'cur_%s_small.png' % n)
    im2.save(p)
    print(p, im.size, '->', im2.size)
