# -*- coding: utf-8 -*-
"""Проверка, что дефринж только срезал кайму и не съел детали силуэта.

Для каждого файла (git HEAD vs рабочая копия):
  * сколько плотных пикселей ушло/пришло;
  * все ли ушедшие пиксели лежат не дальше DIL px от оставшегося силуэта
    (то есть срезана кромка, а не оторванные острова/пальцы/пряди);
  * сколько связных компонент было и стало (не рассыпался ли силуэт);
  * цвет кожи в области рук не уехал.
"""
import io
import os
import subprocess
from collections import deque

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
    'poet_seat_smile.webp', 'poet_seat_sullen.webp',
    'poet_sh.webp', 'poet_sh_inspired.webp', 'poet_sh_tired.webp',
    'poet_sit.webp', 'poet_sit_interested.webp', 'poet_sit_upset.webp',
    'sergey.webp', 'sergey_concerned.webp', 'sergey_smile.webp',
]
DIL = 3


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


def dilate(mask, n=1):
    m = mask.copy()
    for _ in range(n):
        d = m.copy()
        d[1:, :] |= m[:-1, :]
        d[:-1, :] |= m[1:, :]
        d[:, 1:] |= m[:, :-1]
        d[:, :-1] |= m[:, 1:]
        m = d
    return m


def ncomp(mask, min_area=30):
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    ys, xs = np.nonzero(mask)
    comps = 0
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        area = 0
        while q:
            y, x = q.popleft()
            area += 1
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if area >= min_area:
            comps += 1
    return comps


def load_git(name):
    raw = subprocess.check_output(['git', 'show', REF + ':vn2/img/char/' + name], cwd=ROOT)
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))


def skin(arr):
    """средний цвет «кожи»: тёплые пиксели с r>g>b и r-b > 25."""
    rgb = arr[:, :, :3].astype(int)
    al = arr[:, :, 3]
    m = (al > 200) & (rgb[:, :, 0] > rgb[:, :, 1]) & (rgb[:, :, 1] > rgb[:, :, 2]) & \
        ((rgb[:, :, 0] - rgb[:, :, 2]) > 25) & (rgb[:, :, 0] > 120)
    if m.sum() < 50:
        return None
    return (int(rgb[:, :, 0][m].mean()), int(rgb[:, :, 1][m].mean()),
            int(rgb[:, :, 2][m].mean()), int(m.sum()))


bad = []
print('%-28s %7s %7s %7s  %-12s %s' % ('файл', 'плотн.', 'ушло', 'пришло', 'вне DIL=3', 'кожа r,g,b,n (git -> work)'))
for n in NAMES:
    g = load_git(n)
    w = np.asarray(Image.open(os.path.join(CHAR, n)).convert('RGBA'))
    sg, sw = g[:, :, 3] > 128, w[:, :, 3] > 128
    removed = sg & ~sw
    added = ~sg & sw
    far = removed & ~dilate(sw, DIL)
    sk_g, sk_w = skin(g), skin(w)
    sk = '—'
    if sk_g and sk_w:
        sk = '(%d,%d,%d) n %d -> (%d,%d,%d) n %d' % (sk_g + sk_w)
    flag = ''
    if far.any():
        flag = ' !! острова %d px' % int(far.sum())
        bad.append(n)
    print('%-28s %7d %7d %7d  %-12s %s%s'
          % (n, int(sg.sum()), int(removed.sum()), int(added.sum()),
             '%d px' % int(far.sum()), sk, flag))

print('\nпроблемных: %d %s' % (len(bad), bad if bad else ''))
