# -*- coding: utf-8 -*-
"""Превью v5: скамейка чуть правее и ниже, задняя левая ножка — у бордюра НА асфальте;
поэт посажен по ЗАМЕРУ своей линии сиденья, а не по старой константе.

Что замерено (модель со зрением, `_alley_measure_vision.py`, сетка на картинке):
  • у пропа `bench.webp` задняя левая ножка = (x 0.10, y 0.88) файла — это и есть
    «земля у ближнего торца», которую двигаем к бордюру;
  • у спрайта поэта линия таза на сиденье = y 0.595 высоты спрайта, ступни = 0.985.
    Старая константа 0.346 (от фигуры) давала 0.696 высоты — на 0.10 спрайта НИЖЕ
    настоящей линии, из-за этого таз садился выше сиденья и поэт «висел».
    Проверка: 0.10 * 619 px ≈ 62 px ровно то, что видно как зазор.

Бордюр: замер по кадру `_alley_path_fit.py` — левый край асфальта
x = 0.2856*y - 108.5 (1920x1080).

Скамейка ставится так, чтобы ножка (0.10, 0.88) попала в (X_LEG, Y_LEG), где X_LEG
чуть правее бордюра в этой строке (то есть уже на асфальте). Масштаб из перспективы:
m(y) = 1.146*(y - 572) px/м; сиденье 0.45 м, спинка 0.90 м.

Запуск: python3 _alley_prev5.py   (крутилки — переменные окружения)
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146           # m(y) = K*(y - Y_H) px/м

# --- положение скамейки (по слову Ивана: чуть правее и чуть ниже v4)
Y_LEG = float(os.environ.get('Y_LEG', 960))     # y земли у задней левой ножки
CURB_INSET = float(os.environ.get('CURB_INSET', 20))   # на сколько px внутрь асфальта
SEAT_H, BACK_H = 0.45, 0.90
AXIS_DEG = 26.2                 # собственная перспектива пропа (замер по маске)
AXIS = np.deg2rad(AXIS_DEG)

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
PROP = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')
os.makedirs(OUT, exist_ok=True)

# доли файла пропа
LEG_X_F, LEG_Y_F = 0.10, 0.881
SEAT_X_F, SEAT_Y_F = 0.10, 0.521
# доли файла поэта (замер со зрением)
P_SEAT_F, P_FEET_F = 0.595, 0.985
ALONG_M = 0.504                 # 28 % длины скамейки от ближнего торца

curb_x = 0.2856 * Y_LEG - 108.5
X_LEG = curb_x + CURB_INSET
m = K * (Y_LEG - Y_H)
print('глубина ножки y=%.0f: бордюр x=%.0f, ножка x=%.0f (+%.0f px внутрь асфальта)'
      % (Y_LEG, curb_x, X_LEG, CURB_INSET))
print('масштаб %.0f px/м на этой глубине' % m)

# --- масштаб пропа: спинка 0.90 м = (LEG_Y_F - BACK_TOP_F) высоты файла
BACK_TOP_F = 0.160
h_file = BACK_H * m / (LEG_Y_F - BACK_TOP_F)
prop = Image.open(PROP).convert('RGBA')
prop = prop.resize((max(1, round(prop.width * h_file / prop.height)), max(1, round(h_file))),
                   Image.LANCZOS)
paste_x = int(round(X_LEG - LEG_X_F * prop.width))
paste_y = int(round(Y_LEG - LEG_Y_F * prop.height))
print('проп %dx%d, вставка в (%d,%d), bbox до (%d,%d)'
      % (prop.width, prop.height, paste_x, paste_y, paste_x + prop.width, paste_y + prop.height))

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


put_center_left(bg, KATE, 73, 99, -3)
bg.alpha_composite(prop, (paste_x, paste_y))

# --- линия сиденья в экране: точка над ножкой + ось
seat0 = (X_LEG, Y_LEG - SEAT_H * m)
print('сиденье над задней ножкой: (%.0f, %.0f)' % seat0)

# --- поэт: масштаб из условия «таз на сиденье, ступни на земле»
span_px = (P_FEET_F - P_SEAT_F) * 1.0     # в долях высоты спрайта
need = SEAT_H * m                          # столько px от сиденья до земли
ph = need / span_px
poet = Image.open(POET).convert('RGBA')
pw = round(poet.width * ph / poet.height)
poet = poet.resize((pw, max(1, round(ph))), Image.LANCZOS)
ph = poet.height
print('поэт: высота спрайта %.0f px (таз-ступни %.0f px = %.2f м), ширина %d'
      % (ph, need, SEAT_H, pw))
print('  видимая фигура %.0f px = %.2f м (было бы у человека ~1.35 м сидя)'
      % ((P_FEET_F - 0.14) * ph, (P_FEET_F - 0.14) * ph / m))

along_px = ALONG_M * m
seat_x = seat0[0] + along_px * np.cos(AXIS)
seat_y = seat0[1] - along_px * np.sin(AXIS)
ground_y = Y_LEG - (seat_x - X_LEG) * np.tan(AXIS)
px = int(round(seat_x - pw / 2.0))
py = int(round(ground_y - P_FEET_F * ph))
print('посадка: сиденье (%.0f, %.0f), земля под ним %.0f' % (seat_x, seat_y, ground_y))
print('вставка поэта (%d,%d), таз окажется на y=%.0f (сиденье %.0f), ступни y=%.0f (земля %.0f)'
      % (px, py, py + P_SEAT_F * ph, seat_y, py + P_FEET_F * ph, ground_y))
bg.alpha_composite(poet, (px, py))

p1 = os.path.join(OUT, 'alley_prev5.jpg')
bg.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p1, quality=88)
p2 = os.path.join(OUT, 'alley_prev5_full.jpg')
bg.convert('RGB').save(p2, quality=90)
print('saved', os.path.relpath(p1, HERE), os.path.getsize(p1), 'B')
print('saved', os.path.relpath(p2, HERE), os.path.getsize(p2), 'B')
