# -*- coding: utf-8 -*-
"""Превью v8: скамейка ближе к бордюру, поэт посажен по ПРАВИЛЬНОЙ доле таза.

Ошибка, из-за которой поэт был мелкий: линию таза я взял из ответа модели со зрением
(0.595 высоты файла), а замер маски самого спрайта (`_poet_profile.py`) даёт другое:
  • фигура занимает y 201..1418 из 1433 (доля 0.140…0.990);
  • бёдра = 0.346 высоты ФИГУРЫ от ступней — то есть ровно та константа, что стояла
    в старом `_alley_layout.py`, а не 0.536, как вышло по ответу модели.
Пересчёт: 0.990 - 0.346*(0.990-0.140) = 0.696 доли файла — это линия таза.
Со спрайтом 515 px (как в v7) видимая фигура выходила 0.98 м, отсюда «слишком маленький».

Сейчас масштаб берётся из высоты сиденья: сиденье 0.45 м над землёй = 0.346 фигуры
-> фигура = 1.30 м, спрайт ≈ 680 px (было 515).

Скамейка: X_LEG 186 -> 170 (на 16 px ближе к бордюру, по слову Ивана «чуть назад»).
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146
VANISH = (1037.0, 572.0)

Y_LEG = float(os.environ.get('Y_LEG', 960))
X_LEG = float(os.environ.get('X_LEG', 170))
LEG_X_F, LEG_Y_F = 0.10, 0.881
BACK_TOP_F = 0.160
SEAT_F, GROUND_F = 0.624, 0.986
BUTT_FX = float(os.environ.get('BUTT_FX', 0.295))
BACK_H = 0.90

# доли файла спрайта поэта (замер маски)
P_HEAD_F, P_FEET_F = 201.0 / 1433.0, 1419.0 / 1433.0
HIP_OF_FIGURE = 0.346          # таз от ступней, в долях фигуры
P_BUTT_F = P_FEET_F - HIP_OF_FIGURE * (P_FEET_F - P_HEAD_F)

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
PROP = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

alley_deg = np.degrees(np.arctan2(Y_LEG - VANISH[1], VANISH[0] - X_LEG))
ROT = alley_deg - 26.2
m = K * (Y_LEG - Y_H)
h_file = BACK_H * m / (LEG_Y_F - BACK_TOP_F)
prop0 = Image.open(PROP).convert('RGBA')
prop0 = prop0.resize((max(1, round(prop0.width * h_file / prop0.height)),
                      max(1, round(h_file))), Image.LANCZOS)
ax, ay = LEG_X_F * prop0.width, LEG_Y_F * prop0.height
prop = prop0.rotate(ROT, resample=Image.BICUBIC, expand=True, center=(ax, ay))
th = np.deg2rad(ROT)
cx, cy = prop0.width / 2.0, prop0.height / 2.0


def moved(px, py):
    x, y = px - cx, py - cy
    return (x * np.cos(th) + y * np.sin(th) + prop.width / 2.0,
            -x * np.sin(th) + y * np.cos(th) + prop.height / 2.0)


a_new = moved(ax, ay)
paste = (int(round(X_LEG - a_new[0])), int(round(Y_LEG - a_new[1])))
seat_pt = moved(BUTT_FX * prop0.width, SEAT_F * prop0.height)
ground_pt = moved(BUTT_FX * prop0.width, GROUND_F * prop0.height)
seat_x, seat_y = paste[0] + seat_pt[0], paste[1] + seat_pt[1]
ground_y = paste[1] + ground_pt[1]
print('скамейка: поворот %.1f°, вставка (%d,%d)' % (ROT, paste[0], paste[1]))
print('посадка (%.0f, %.0f), земля %.0f, высота сиденья %.0f px = %.2f м'
      % (seat_x, seat_y, ground_y, ground_y - seat_y, (ground_y - seat_y) / m))

bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')


def put_center_left(canvas, path, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
    im = Image.open(path).convert('RGBA')
    h = round(H * height_pct / 100.0)
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    canvas.alpha_composite(im, (round(W * left_pct / 100.0 - w / 2.0),
                                round(H * (1.0 - bottom_pct / 100.0)) - h))


put_center_left(bg, KATE, 73, 99, -3)
bg.alpha_composite(prop, paste)

poet = Image.open(POET).convert('RGBA')
fig_px = (ground_y - seat_y) / HIP_OF_FIGURE          # фигура от ступней до макушки
ph = int(round(fig_px / (P_FEET_F - P_HEAD_F)))
pw = round(poet.width * ph / poet.height)
poet = poet.resize((pw, max(1, ph)), Image.LANCZOS)
ph = poet.height
py = int(round(ground_y - P_FEET_F * ph))
px = int(round(seat_x - pw / 2.0))
bg.alpha_composite(poet, (px, py))
print('поэт: спрайт %dx%d в (%d,%d), фигура %.0f px = %.2f м'
      % (pw, ph, px, py, (P_FEET_F - P_HEAD_F) * ph, (P_FEET_F - P_HEAD_F) * ph / m))
print('  таз y=%.0f (сиденье %.0f, %+.0f px), ступни y=%.0f (земля %.0f, %+.0f px)'
      % (py + P_BUTT_F * ph, seat_y, py + P_BUTT_F * ph - seat_y,
         py + P_FEET_F * ph, ground_y, py + P_FEET_F * ph - ground_y))
print('  макушка y=%.0f, т.е. на %.2f м над землёй (человек сидя 1.30 м)'
      % (py + P_HEAD_F * ph, (ground_y - (py + P_HEAD_F * ph)) / m))

p1 = os.path.join(OUT, 'alley_prev8.jpg')
bg.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p1, quality=88)
bg.convert('RGB').save(os.path.join(OUT, 'alley_prev8_full.jpg'), quality=90)
print('saved', os.path.relpath(p1, HERE), os.path.getsize(p1), 'B')
