# -*- coding: utf-8 -*-
"""Что реально нарисовано в слоте 0/1: яркость/насыщенность области + наличие
почти-белой «плашки» (признак неудачного вырезания фона)."""
import os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '.tmp_vo')

for f in sorted(os.listdir(D)):
    if not f.startswith('shot_p'):
        continue
    im = Image.open(os.path.join(D, f)).convert('RGB')
    a = np.asarray(im, np.float32)
    h, w, _ = a.shape
    # левый слот: центр x=50% (solo) полоса 22..78%, верх 5..75%
    box = a[int(h * .05):int(h * .78), int(w * .22):int(w * .78)]
    white = ((box > 235).all(2)).mean()
    print('%-14s %s mean=%.1f white=%.1f%%'
          % (f, im.size, box.mean(), 100 * white))
