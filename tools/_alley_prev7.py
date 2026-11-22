# -*- coding: utf-8 -*-
"""Превью v7: скамейка повёрнута так, чтобы её ось совпала с направлением аллеи.

Критик v6 сказал «поперёк перспективы». Причина измеримая: ось пропа в его файле идёт
под 26°, а направление аллеи в кадре — прямая от левого бордюра внизу к точке схода
(ворота ~ x 0.54, y 0.53): наклон 19°. Разница 7° и читается как «поперёк».

Здесь: проп поворачивается на -7° вокруг земли задней левой ножки, поэт сажается на
повёрнутую доску сиденья и ставится ступнями на ту же землю.
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
X_LEG = float(os.environ.get('X_LEG', 186))
LEG_X_F, LEG_Y_F = 0.10, 0.881
BACK_TOP_F = 0.160
SEAT_F, GROUND_F = 0.624, 0.986
P_SEAT_F, P_FEET_F = 0.595, 0.985
BUTT_FX = float(os.environ.get('BUTT_FX', 0.295))   # x таза в долях файла пропа
BACK_H = 0.90

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
PROP = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

# наклон аллеи в кадре
alley_deg = np.degrees(np.arctan2(Y_LEG - VANISH[1], VANISH[0] - X_LEG))
PROP_AXIS = 26.2
ROT = alley_deg - PROP_AXIS           # отрицательный: повернуть по часовой
print('направление аллеи %.1f°, ось пропа %.1f° -> поворот %.1f°' % (alley_deg, PROP_AXIS, ROT))

m = K * (Y_LEG - Y_H)
h_file = BACK_H * m / (LEG_Y_F - BACK_TOP_F)
prop0 = Image.open(PROP).convert('RGBA')
prop0 = prop0.resize((max(1, round(prop0.width * h_file / prop0.height)),
                      max(1, round(h_file))), Image.LANCZOS)

ax, ay = LEG_X_F * prop0.width, LEG_Y_F * prop0.height
prop = prop0.rotate(abs(ROT) * (-1 if ROT > 0 else 1), resample=Image.BICUBIC, expand=True,
                    center=(ax, ay)) if False else prop0.rotate(ROT, resample=Image.BICUBIC,
                                                                expand=True, center=(ax, ay))

# куда уехали точки при повороте с expand
th = np.deg2rad(ROT)
cx, cy = prop0.width / 2.0, prop0.height / 2.0


def moved(px, py):
    x = px - cx
    y = py - cy
    nx = x * np.cos(th) + y * np.sin(th)
    ny = -x * np.sin(th) + y * np.cos(th)
    return nx + prop.width / 2.0, ny + prop.height / 2.0


a_new = moved(ax, ay)
paste = (int(round(X_LEG - a_new[0])), int(round(Y_LEG - a_new[1])))
seat_pt = moved(BUTT_FX * prop0.width, SEAT_F * prop0.height)
ground_pt = moved(BUTT_FX * prop0.width, GROUND_F * prop0.height)
seat_x, seat_y = paste[0] + seat_pt[0], paste[1] + seat_pt[1]
ground_y = paste[1] + ground_pt[1]
print('проп %dx%d, вставка (%d,%d)' % (prop.width, prop.height, paste[0], paste[1]))
print('точка посадки: (%.0f, %.0f); земля под ней y=%.0f; высота сиденья %.0f px = %.2f м'
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
ph = int(round((ground_y - seat_y) / (P_FEET_F - P_SEAT_F)))
pw = round(poet.width * ph / poet.height)
poet = poet.resize((pw, ph), Image.LANCZOS)
px = int(round(seat_x - pw / 2.0))
py = int(round(seat_y - P_SEAT_F * ph))
bg.alpha_composite(poet, (px, py))
print('поэт: спрайт %dx%d в (%d,%d); таз %+.0f px от сиденья, ступни %+.0f px от земли'
      % (pw, ph, px, py, py + P_SEAT_F * ph - seat_y, py + P_FEET_F * ph - ground_y))
print('  видимая фигура %.0f px = %.2f м' % ((P_FEET_F - 0.14) * ph, (P_FEET_F - 0.14) * ph / m))

p1 = os.path.join(OUT, 'alley_prev7.jpg')
bg.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p1, quality=88)
p2 = os.path.join(OUT, 'alley_prev7_full.jpg')
bg.convert('RGB').save(p2, quality=90)
print('saved', os.path.relpath(p1, HERE), os.path.getsize(p1), 'B')
