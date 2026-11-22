# -*- coding: utf-8 -*-
"""Вставка НОВОЙ скамейки в сцену (v10): ось по линии низа, масштаб по ближнему торцу.

Замеры матированного пропа `_sat/prop_bench_new_matte.png` (1407x996):
  • низа по колонкам: (98, 868) -> (1294, 443) => линия земли 19.6° вверх-вправо;
  • верх: (98, 129) -> (1364, 258) => верх уходит вниз, к горизонту (перспектива верна);
  • высота ближнего торца 739 px = 0.90 м => 821 px/м в файле;
  • сиденье 0.45 м над землёй, то есть на середине высоты торца.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146
VANISH = (1037.0, 572.0)

PROP = os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png')
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

Y_LEG = float(os.environ.get('Y_LEG', 960))
X_LEG = float(os.environ.get('X_LEG', 148))
BACK_H = 0.90
AXIS_DEG = 19.6                 # линия земли пропа (замер)
LEG_X_F, LEG_Y_F = 98.0 / 1407.0, 868.0 / 996.0
TOP_Y_F = 129.0 / 996.0
P_HEAD_F, P_FEET_F, P_BUTT_F = 201 / 1433.0, 1419 / 1433.0, 0.625

alley_deg = np.degrees(np.arctan2(Y_LEG - VANISH[1], VANISH[0] - X_LEG))
ROT = alley_deg - AXIS_DEG
m = K * (Y_LEG - Y_H)
need = BACK_H * m
prop0 = Image.open(PROP).convert('RGBA')
k = need / ((LEG_Y_F - TOP_Y_F) * prop0.height)
prop1 = prop0.resize((max(1, round(prop0.width * k)), max(1, round(prop0.height * k))),
                     Image.LANCZOS)
print('сцена %.0f px/м, торец %.0f px, файл x%.3f -> %dx%d, поворот %.1f°'
      % (m, need, k, prop1.width, prop1.height, ROT))

ax, ay = LEG_X_F * prop1.width, LEG_Y_F * prop1.height
prop = prop1.rotate(ROT, resample=Image.BICUBIC, expand=True, center=(ax, ay))
th = np.deg2rad(ROT)
cx, cy = prop1.width / 2.0, prop1.height / 2.0


def moved(px, py):
    x, y = px - cx, py - cy
    return (x * np.cos(th) + y * np.sin(th) + prop.width / 2.0,
            -x * np.sin(th) + y * np.cos(th) + prop.height / 2.0)


a_new = moved(ax, ay)
paste = (int(round(X_LEG - a_new[0])), int(round(Y_LEG - a_new[1])))
seat_near_y = Y_LEG - need * 0.5
along = float(os.environ.get('ALONG_M', 0.50)) * m
A = np.deg2rad(AXIS_DEG)
seat_x = X_LEG + along * np.cos(A)
seat_y = seat_near_y - along * np.sin(A)
print('вставка (%d,%d); сиденье у торца y=%.0f; у поэта (%.0f, %.0f)'
      % (paste[0], paste[1], seat_near_y, seat_x, seat_y))

bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')


def put(canvas, path, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
    im = Image.open(path).convert('RGBA')
    h = round(H * height_pct / 100.0)
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    canvas.alpha_composite(im, (round(W * left_pct / 100.0 - w / 2.0),
                                round(H * (1.0 - bottom_pct / 100.0)) - h))


put(bg, KATE, 73, 99, -3)
bg.alpha_composite(prop, paste)
print('проп bbox (%d,%d)-(%d,%d)' % (paste[0], paste[1],
                                     paste[0] + prop.width, paste[1] + prop.height))

poet = Image.open(POET).convert('RGBA')
ph = int(os.environ.get('POET_H', 780))
pw = round(poet.width * ph / poet.height)
poet = poet.resize((pw, ph), Image.LANCZOS)
px = int(round(seat_x - pw / 2.0))
py = int(round(seat_y - P_BUTT_F * ph))
bg.alpha_composite(poet, (px, py))
print('поэт %d px в (%d,%d); таз y=%.0f (сиденье %.0f), ступни y=%.0f'
      % (ph, px, py, py + P_BUTT_F * ph, seat_y, py + P_FEET_F * ph))

p = os.path.join(OUT, 'alley_prev10.jpg')
bg.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p, quality=88)
bg.convert('RGB').save(os.path.join(OUT, 'alley_prev10_full.jpg'), quality=90)
print('saved', os.path.relpath(p, HERE), os.path.getsize(p), 'B')
