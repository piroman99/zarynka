# -*- coding: utf-8 -*-
"""Сетка кропов 1:1 «до/после» — по три спрайта в ряд, без масштабирования.

Каждый кроп берётся по самому крупному кластеру светлой кромки в исходнике,
то есть показывает ровно то место, где кайма и была. Фон тёмно-серый.
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
OUT = os.path.join(ROOT, '_sat', 'defringe_zoom_grid.png')
REF = os.environ.get('REF', '0e50695')

NAMES = [
    'poet.webp', 'poet_interested.webp', 'poet_upset.webp',
    'poet_seat.webp', 'poet_seat_interested.webp', 'poet_seat_shy.webp',
    'poet_seat_smile.webp', 'poet_seat_sullen.webp', 'poet_seat_upset.webp',
    'poet_sh.webp', 'poet_sh_inspired.webp', 'poet_sh_tired.webp',
    'poet_sit.webp', 'poet_sit_interested.webp', 'poet_sit_upset.webp',
    'sergey.webp', 'sergey_concerned.webp', 'sergey_smile.webp',
]
Z = 190          # сторона кропа, 1:1
PER_ROW = 3
PAD = 10
LBL = 18
BG = (40, 40, 44)


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


def load_ref(name):
    raw = subprocess.check_output(['git', 'show', REF + ':vn2/img/char/' + name], cwd=ROOT)
    return Image.open(io.BytesIO(raw)).convert('RGBA')


def fringe_box(arr):
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
    # только ВНЕШНЯЯ кромка: пиксели, рядом с которыми есть полная прозрачность.
    # внутренние светлые края (прядь на тёмном пиджаке) — не кайма и для листа не годятся.
    light = light & dilate(al < 20, 4)
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


def crop_sq(im, box):
    """квадрат Z×Z с центром в кластере кромки, внутри границ картинки."""
    cx = (box[0] + box[2]) // 2
    cy = (box[1] + box[3]) // 2
    x0 = max(0, min(im.width - Z, cx - Z // 2))
    y0 = max(0, min(im.height - Z, cy - Z // 2))
    part = im.crop((x0, y0, min(im.width, x0 + Z), min(im.height, y0 + Z)))
    out = Image.new('RGBA', (Z, Z), BG + (255,))
    out.alpha_composite(part, (0, 0))
    return out.convert('RGB')


rows = (len(NAMES) + PER_ROW - 1) // PER_ROW
CELLW = 2 * Z + PAD
W = PAD + PER_ROW * (CELLW + PAD)
H = PAD + rows * (Z + LBL + PAD)
sheet = Image.new('RGB', (W, H), (26, 26, 30))
d = ImageDraw.Draw(sheet)

skipped = []
for i, name in enumerate(NAMES):
    r, c = divmod(i, PER_ROW)
    before = load_ref(name)
    after = Image.open(os.path.join(CHAR, name)).convert('RGBA')
    box = fringe_box(np.asarray(before))
    if box is None:
        skipped.append(name)
        continue
    x = PAD + c * (CELLW + PAD)
    y = PAD + r * (Z + LBL + PAD)
    sheet.paste(crop_sq(before, box), (x, y))
    sheet.paste(crop_sq(after, box), (x + Z + PAD, y))
    d.text((x, y + Z + 3), name.replace('.webp', '') + '   ДО | ПОСЛЕ', fill=(215, 215, 215))

sheet.save(OUT)
print('сетка: %s  %dx%d  %.2f МБ' % (os.path.relpath(OUT, ROOT), sheet.width, sheet.height,
                                     os.path.getsize(OUT) / 1048576.0))
if skipped:
    print('не нашёл кластера кромки:', skipped)
