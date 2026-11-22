# -*- coding: utf-8 -*-
"""Лист «до/после» для дефринжа: 17 спрайтов, каждый в 4 клетки.

    [ до, весь ]  [ после, весь ]  [ до, 1:1 ]  [ после, 1:1 ]

Фон тёмно-серый: белая кайма видна именно на нём (на светлом её не разглядеть).
Кроп 1:1 берётся по САМОМУ КРУПНОМУ кластеру светлой кромки в исходнике —
то есть показывается ровно то место, где кайма и была.
"""
import io
import os
import subprocess
from collections import deque

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHAR = os.path.join(ROOT, 'vn2', 'img', 'char')
OUT = os.path.join(ROOT, '_sat', 'defringe_before_after.png')

NAMES = [
    'poet.webp', 'poet_interested.webp', 'poet_upset.webp',
    'poet_seat.webp', 'poet_seat_interested.webp', 'poet_seat_shy.webp',
    'poet_seat_smile.webp', 'poet_seat_sullen.webp', 'poet_seat_upset.webp',
    'poet_sh.webp', 'poet_sh_inspired.webp', 'poet_sh_tired.webp',
    'poet_sit.webp', 'poet_sit_interested.webp', 'poet_sit_upset.webp',
    'sergey.webp', 'sergey_concerned.webp', 'sergey_smile.webp',
]
BG = (42, 42, 46)
FULL_H = 230
ZOOM = 230
PAD = 8
LABEL_W = 250

# последний коммит ДО дефринжа (в HEAD спрайты уже обработанные)
REF = '0e50695'


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


def load_git(name):
    raw = subprocess.check_output(['git', 'show', REF + ':vn2/img/char/' + name], cwd=ROOT)
    return Image.open(io.BytesIO(raw)).convert('RGBA')


def fringe_box(arr):
    """bbox самого крупного кластера светлой кромки в исходнике."""
    al = arr[:, :, 3].astype(np.float32)
    rgb = arr[:, :, :3].astype(np.float32)
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    solid = al > 128
    edge = solid & ~erode(solid, 2)
    inner = erode(solid, 2) & ~erode(solid, 6)
    if not inner.any():
        return None
    core = lum[inner].mean()
    light = edge & (lum > core + 35)
    if not light.any():
        return None
    h, w = light.shape
    seen = np.zeros_like(light, bool)
    best, bestn = None, 0
    ys, xs = np.nonzero(light)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        pts = []
        while q:
            y, x = q.popleft()
            pts.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and light[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if len(pts) > bestn:
            bestn, best = len(pts), np.array(pts)
    if best is None:
        return None
    ys, xs = best[:, 0], best[:, 1]
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def bbox_of(im):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if not len(ys):
        return (0, 0, im.width, im.height)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def cell(im, size, crop=None):
    """вписать в квадрат size×size на тёмном фоне (или 1:1 кроп)."""
    out = Image.new('RGBA', (size, size), BG + (255,))
    if crop is None:
        bx = bbox_of(im)
        part = im.crop(bx)
        k = min(size / part.width, size / part.height)
        part = part.resize((max(1, int(part.width * k)), max(1, int(part.height * k))),
                           Image.LANCZOS)
    else:
        part = im.crop(crop)
        if part.width > size or part.height > size:
            part = part.crop((0, 0, min(part.width, size), min(part.height, size)))
    out.alpha_composite(part, ((size - part.width) // 2, (size - part.height) // 2))
    return out.convert('RGB')


rows = []
for name in NAMES:
    before = load_git(name)
    after = Image.open(os.path.join(CHAR, name)).convert('RGBA')
    fb = fringe_box(np.asarray(before))
    if fb is None:
        crop = None
    else:
        cx0, cy0, cx1, cy1 = fb
        pad = 55
        crop = (max(0, cx0 - pad), max(0, cy0 - pad),
                min(before.width, cx1 + pad), min(before.height, cy1 + pad))
    rows.append((name, before, after, crop))

W = LABEL_W + 4 * (ZOOM + PAD) + PAD
H = PAD + len(rows) * (ZOOM + PAD)
sheet = Image.new('RGB', (W, H), (26, 26, 30))
d = ImageDraw.Draw(sheet)
d.text((PAD, 4), 'ДО (%s)                ПОСЛЕ                ДО 1:1                ПОСЛЕ 1:1' % REF,
       fill=(220, 220, 220))

y = PAD + 14
for name, before, after, crop in rows:
    d.text((PAD, y + ZOOM // 2 - 6), name.replace('.webp', ''), fill=(210, 210, 210))
    x = LABEL_W
    for im, cr in ((before, None), (after, None), (before, crop), (after, crop)):
        sheet.paste(cell(im, ZOOM, cr), (x, y))
        x += ZOOM + PAD
    y += ZOOM + PAD

sheet.save(OUT)
print('лист: %s  %dx%d  %.2f МБ' % (os.path.relpath(OUT, ROOT), sheet.width, sheet.height,
                                   os.path.getsize(OUT) / 1048576.0))
