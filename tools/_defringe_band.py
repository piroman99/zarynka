# -*- coding: utf-8 -*-
"""Решающий тест «осталась ли белая матица»: яркость полупрозрачной бахромы
против соседних плотных пикселей.

Если кайма есть, бахрома (альфа 20..200) заметно СВЕТЛЕЕ плотного тела.
После дефринжа цвет бахромы заполнен изнутри, поэтому разница близка к нулю.
Меряется по всему спрайту: REF (до) и рабочая копия (после).
"""
import io
import os
import subprocess

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')
REF = os.environ.get('REF', '0e50695')

NAMES = [
    'poet.webp', 'poet_interested.webp', 'poet_upset.webp',
    'poet_seat.webp', 'poet_seat_interested.webp', 'poet_seat_shy.webp',
    'poet_seat_smile.webp', 'poet_seat_sullen.webp', 'poet_seat_upset.webp',
    'poet_sh.webp', 'poet_sh_inspired.webp', 'poet_sh_tired.webp',
    'poet_sit.webp', 'poet_sit_interested.webp', 'poet_sit_upset.webp',
    'sergey.webp', 'sergey_concerned.webp', 'sergey_smile.webp',
]


def load_ref(name):
    raw = subprocess.check_output(['git', 'show', REF + ':vn2/img/char/' + name], cwd=ROOT)
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))


def band_gap(arr):
    a = arr[:, :, 3].astype(np.float32)
    rgb = arr[:, :, :3].astype(np.float32)
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    band = (a > 20) & (a < 200)
    solid = a > 245
    if band.sum() < 50 or solid.sum() < 500:
        return None
    return float(lum[band].mean()), float(lum[solid].mean()), int(band.sum())


print('%-28s %-28s %-28s %s'
      % ('файл', 'ДО: бахрома/тело', 'ПОСЛЕ: бахрома/тело', 'зазор'))
for n in NAMES:
    b = band_gap(load_ref(n))
    a = band_gap(np.asarray(Image.open(os.path.join(CHAR, n)).convert('RGBA')))
    if b is None or a is None:
        print('%-28s нет данных' % n)
        continue
    print('%-28s %6.1f / %6.1f (%5d px)  %6.1f / %6.1f (%5d px)  %+6.1f -> %+6.1f'
          % (n, b[0], b[1], b[2], a[0], a[1], a[2], b[0] - b[1], a[0] - a[1]))
