# -*- coding: utf-8 -*-
"""Превью v3: проп БЕЗ поворота (его перспектива уже нарисована), меньше, на газоне.

Найдено замером `_prop_axis.py`: в самом файле bench.webp линия земли идёт от
(86, 617) к (686, 322), т.е. наклон ~26° вверх-вправо — скамейка УЖЕ нарисована
уходящей в глубину. В v2 я повернул её ещё на 22° → суммарно ~48°, отсюда «поперёк
дороги и завал» (модель со зрением сказала то же: повернуть обратно на 30–35°).

Правки против v2:
  • поворот 0° (используем нарисованную перспективу);
  • масштаб меньше: спинка 0.90 м по m(y), а не «на глаз»;
  • сдвиг влево в газон (0.06 кадра), чтобы не пересекать бордюр;
  • поэт сажается бёдрами на линию сиденья, сам НЕ наклоняется (вертикали в
    перспективе остаются вертикальными).
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146          # m(y) = K*(y - Y_H) px/м, калибровка по Екатерине

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
PROP = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

Y_GROUND = float(os.environ.get('Y_GROUND', 925))
NEAR_X = float(os.environ.get('NEAR_X', 180))
SEAT_ALONG = 0.28
BENCH_LEN_M, BENCH_BACK_M = 1.8, 0.90

# в файле bench.webp (925x700): земля у ближнего торца y=617, сиденье = земля - 0.45 м
# в пикселях файла; высота ближнего торца (спинка) 617-112 = 505 = 0.90 м -> 561 px/м
FILE_H = 700.0
BACK_TOP_F = 112.0 / FILE_H
GROUND_F = 617.0 / FILE_H
SEAT_F = GROUND_F - (0.45 / 0.90) * (GROUND_F - BACK_TOP_F)
# собственная ось скамейки в файле: наклон ~26°, длина по x 841-6 px
AXIS_DEG = 26.2
AXIS = np.deg2rad(AXIS_DEG)

m = K * (Y_GROUND - Y_H)
back_px = BENCH_BACK_M * m
h_file = back_px / (GROUND_F - BACK_TOP_F)
prop = Image.open(PROP).convert('RGBA')
prop = prop.resize((max(1, round(prop.width * h_file / FILE_H)), max(1, round(h_file))),
                   Image.LANCZOS)
print('глубина y=%.0f -> %.0f px/м; спинка %.0f px; файл пропа %dx%d'
      % (Y_GROUND, m, back_px, prop.width, prop.height))
print('длина 1.8 м = %.0f px по оси, по x %.0f px' % (BENCH_LEN_M * m, BENCH_LEN_M * m * np.cos(AXIS)))

# точка «земля у ближнего торца» внутри файла
gx_f, gy_f = 86.0 / 925.0 * prop.width, GROUND_F * prop.height
print('якорь в файле: (%.0f, %.0f)' % (gx_f, gy_f))
paste = (int(round(NEAR_X - gx_f)), int(round(Y_GROUND - gy_f)))

bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')


def put_center_left(canvas, path, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
    im = Image.open(path).convert('RGBA')
    h = round(H * height_pct / 100.0)
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    top = round(H * (1.0 - bottom_pct / 100.0)) - h
    left = round(W * left_pct / 100.0 - w / 2.0)
    canvas.alpha_composite(im, (left, top))
    return (left, top, left + w, top + h)


kate_bb = put_center_left(bg, KATE, 73, 99, -3)
bg.alpha_composite(prop, paste)
print('проп на экране bbox (%d,%d)-(%d,%d)' % (paste[0], paste[1],
                                               paste[0] + prop.width, paste[1] + prop.height))

# --- поэт
FILL, HIP = 0.85, 0.346
fig_px = 1.30 * m
poet = Image.open(POET).convert('RGBA')
ph = round(fig_px / FILL)
pw = round(poet.width * ph / poet.height)
poet = poet.resize((pw, ph), Image.LANCZOS)
feet_f = 1419.0 / 1433.0 * ph
hip_f = feet_f - HIP * fig_px

# сиденье в экране у ближнего торца и на 28 % длины
seat_near_y = Y_GROUND - (GROUND_F - SEAT_F) * prop.height
along = SEAT_ALONG * BENCH_LEN_M * m
hip_x = NEAR_X + along * np.cos(AXIS)
hip_y = seat_near_y - along * np.sin(AXIS)
print('сиденье у торца y=%.0f; посадка (%.0f, %.0f)' % (seat_near_y, hip_x, hip_y))
print('фигура поэта %.0f px (1.30 м), холст %dx%d' % (fig_px, pw, ph))

px = int(round(hip_x - pw / 2.0))
py = int(round(hip_y - hip_f))
bg.alpha_composite(poet, (px, py))
print('поэт bbox (%d,%d)-(%d,%d), ступни на y=%.0f' % (px, py, px + pw, py + ph, py + feet_f))
print('земля под ступнями вдоль скамейки: %.0f' % (Y_GROUND - (hip_x - NEAR_X) * np.tan(AXIS)))

p1 = os.path.join(OUT, 'alley_prev3.jpg')
bg.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p1, quality=88)
print('saved', os.path.relpath(p1, HERE), os.path.getsize(p1), 'B')
p2 = os.path.join(OUT, 'alley_prev3_full.jpg')
bg.convert('RGB').save(p2, quality=90)
print('saved', os.path.relpath(p2, HERE), os.path.getsize(p2), 'B')
