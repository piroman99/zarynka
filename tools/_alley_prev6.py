# -*- coding: utf-8 -*-
"""Превью v6: поэт сажается по НАРИСОВАННОМУ сиденью пропа, а не по «0.45 м от земли».

Почему v5 не годился: таз ставился на Y_LEG - 0.45*m, а Y_LEG — это земля у ЗАДНЕЙ
левой ножки, которая дальше от камеры. В перспективе её земля выше по кадру, поэтому
высота сиденья получалась заниженной на ~0.1 высоты пропа — поэт и висел.

Как мерил (своими пикселями, `_prop_ascii.py` — карта маски bench.webp 925x700):
  • доска сиденья у ближнего торца — сплошная горизонтальная полоса, строки 437..490,
    по x от ~65 до ~342 файла. Верх доски y=437 (доля 0.624);
  • ножки под ней: задняя левая (x 65..130) доходит до y=610 (доля 0.871),
    передняя левая (x 305..380) — до y=690 (доля 0.986). Земля у ближнего торца,
    то есть там, где стоят ступни сидящего, — 0.986;
  • высота сиденья над землёй выходит 690-437 = 253 px файла = 0.45 м при 561 px/м —
    то есть рисунок сам согласован, ошибалась только моя формула привязки.

Скамейка: как просил Иван — правее и ниже v4, задняя левая ножка (доля 0.10/0.881)
на асфальте у бордюра.

Крутилки: SEAT_F (доля файла, верх доски), GROUND_F (доля файла, земля у передней
ножки), POET_H (высота спрайта, px), BUTT_X (x таза на экране).
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146

Y_LEG = float(os.environ.get('Y_LEG', 960))       # земля у задней левой ножки
X_LEG = float(os.environ.get('X_LEG', 186))       # её x (правее бордюра, на асфальте)
LEG_X_F, LEG_Y_F = 0.10, 0.881
BACK_TOP_F = 0.160
SEAT_F = float(os.environ.get('SEAT_F', 0.624))    # верх доски сиденья (замер)
GROUND_F = float(os.environ.get('GROUND_F', 0.986))  # земля у передней ножки (замер)
P_SEAT_F, P_FEET_F = 0.595, 0.985                  # у спрайта поэта (замер со зрением)
BUTT_X = float(os.environ.get('BUTT_X', 330))      # x таза на экране
POET_H = os.environ.get('POET_H')                  # если задано — фиксируем высоту спрайта
BACK_H = 0.90

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
PROP = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

m = K * (Y_LEG - Y_H)
h_file = BACK_H * m / (LEG_Y_F - BACK_TOP_F)
prop = Image.open(PROP).convert('RGBA')
prop = prop.resize((max(1, round(prop.width * h_file / prop.height)), max(1, round(h_file))),
                   Image.LANCZOS)
paste = (int(round(X_LEG - LEG_X_F * prop.width)), int(round(Y_LEG - LEG_Y_F * prop.height)))
print('глубина ножки y=%.0f -> %.0f px/м; проп %dx%d в (%d,%d)'
      % (Y_LEG, m, prop.width, prop.height, paste[0], paste[1]))

seat_y = paste[1] + SEAT_F * prop.height
ground_y = paste[1] + GROUND_F * prop.height
print('верх доски сиденья на экране y=%.0f, земля у передней ножки y=%.0f, разница %.0f px = %.2f м'
      % (seat_y, ground_y, ground_y - seat_y, (ground_y - seat_y) / m))

bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')


def put_center_left(canvas, path, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
    im = Image.open(path).convert('RGBA')
    h = round(H * height_pct / 100.0)
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    top = round(H * (1.0 - bottom_pct / 100.0)) - h
    left = round(W * left_pct / 100.0 - w / 2.0)
    canvas.alpha_composite(im, (left, top))


put_center_left(bg, KATE, 73, 99, -3)
bg.alpha_composite(prop, paste)

poet = Image.open(POET).convert('RGBA')
if POET_H:
    ph = int(POET_H)
else:
    ph = int(round((ground_y - seat_y) / (P_FEET_F - P_SEAT_F)))
pw = round(poet.width * ph / poet.height)
poet = poet.resize((pw, ph), Image.LANCZOS)
px = int(round(BUTT_X - pw / 2.0))
py = int(round(seat_y - P_SEAT_F * ph))
bg.alpha_composite(poet, (px, py))
print('поэт: спрайт %dx%d, вставка (%d,%d)' % (pw, ph, px, py))
print('  таз y=%.0f (сиденье %.0f, разница %+.0f px), ступни y=%.0f (земля %.0f, %+.0f px)'
      % (py + P_SEAT_F * ph, seat_y, py + P_SEAT_F * ph - seat_y,
         py + P_FEET_F * ph, ground_y, py + P_FEET_F * ph - ground_y))
print('  видимая фигура %.0f px = %.2f м (человек сидя ~1.35 м)'
      % ((P_FEET_F - 0.14) * ph, (P_FEET_F - 0.14) * ph / m))

p1 = os.path.join(OUT, 'alley_prev6.jpg')
bg.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p1, quality=88)
p2 = os.path.join(OUT, 'alley_prev6_full.jpg')
bg.convert('RGB').save(p2, quality=90)
print('saved', os.path.relpath(p1, HERE), os.path.getsize(p1), 'B')
