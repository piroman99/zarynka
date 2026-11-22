# -*- coding: utf-8 -*-
"""Метрика «белая кайма»: яркость внешнего кольца силуэта против кольца 2..5 px внутри.

Кайма от вырезания по белому даёт систематическое превышение на 1 px кромке
(белое подмешано только в край). Светлый КОНТЕНТ (руки, блики) присутствует
и на кольце внутри, поэтому дельта остаётся около нуля.

Печатает для каждого файла: git-версию (исходник) и рабочую (после обработки).
"""
import io
import os
import subprocess

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')

# последний коммит ДО дефринжа: в HEAD спрайты уже обработанные
REF = os.environ.get('REF', '0e50695')

NAMES = [
    'poet.webp', 'poet_interested.webp', 'poet_upset.webp',
    'poet_seat.webp', 'poet_seat_interested.webp', 'poet_seat_shy.webp',
    'poet_seat_smile.webp', 'poet_seat_sullen.webp', 'poet_seat_upset.webp',
    'poet_sh.webp', 'poet_sh_inspired.webp', 'poet_sh_tired.webp',
    'poet_sit.webp', 'poet_sit_interested.webp', 'poet_sit_upset.webp',
    'sergey.webp', 'sergey_concerned.webp', 'sergey_smile.webp',
    'kate.webp', 'kate_sad.webp', 'kate_smile.webp', 'starik_stern.webp',
]


def erode(mask, n=1):
    m = mask.copy()
    for _ in range(n):
        e = m.copy()
        e[1:, :] &= m[:-1, :]
        e[:-1, :] &= m[1:, :]
        e[:, 1:] &= m[:, :-1]
        e[:, :-1] &= m[:, 1:]
        m = e
    return m


def ring_delta(arr):
    al = arr[:, :, 3].astype(np.float32)
    rgb = arr[:, :, :3].astype(np.float32)
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    solid = al > 200
    if solid.sum() < 100:
        return None
    r0 = solid & ~erode(solid, 1)
    r1 = erode(solid, 2) & ~erode(solid, 5)
    if not r1.any():
        return None
    return dict(edge=float(lum[r0].mean()), inner=float(lum[r1].mean()),
                delta=float(lum[r0].mean() - lum[r1].mean()),
                n0=int(r0.sum()), n1=int(r1.sum()))


def load_git(name):
    try:
        raw = subprocess.check_output(['git', 'show', REF + ':vn2/img/char/' + name],
                                      cwd=ROOT, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))


print('%-28s %-22s %-22s %s' % ('файл', REF + ': кромка/внутри', 'сейчас: кромка/внутри', 'Δ каймы'))
for n in NAMES:
    g = load_git(n)
    w = np.asarray(Image.open(os.path.join(CHAR, n)).convert('RGBA'))
    sg, sw = ring_delta(g), ring_delta(w)
    if sg is None or sw is None:
        print('%-28s нет данных' % n)
        continue
    print('%-28s %6.1f / %6.1f %+6.1f  %6.1f / %6.1f %+6.1f  %+.1f'
          % (n, sg['edge'], sg['inner'], sg['delta'],
             sw['edge'], sw['inner'], sw['delta'], sw['delta'] - sg['delta']))
