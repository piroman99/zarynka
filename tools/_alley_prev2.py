# -*- coding: utf-8 -*-
"""Превью v2: скамейка ВДОЛЬ левого края аллеи, меньше размером, с наклоном по перспективе.

Что не так было в v1 (слова Ивана): «слишком большая и поперёк дороги, и не у тротуара.
Должна быть вдоль него».

Замеры фона (`_alley_road_ascii.py`, `_alley_path_fit.py`) и разбор кадра моделью со
зрением: аллея идёт от камеры в глубину к кованым воротам, точка схода ~ (1035, 560)
в кадре 1920x1080; слева и справа от дороги — газон с елями и бордюр.

Поэтому:
  • ось скамейки направлена К точке схода (а не поперёк): наклон +25° (вверх-вправо);
  • размер взят из перспективы, а не «на глаз»: спинка 0.90 м, длина 1.8 м,
    масштаб m(y) = 1.146*(y - 572) px/м калиброван по Екатерине (1.70 м = 619 px);
  • земля ближнего торца ставится на y_ground, ближний торец — у левого края газона;
  • поэт масштабируется в ту же глубину (1.30 м сидя) и наклоняется вместе со скамейкой.

Печатает все числа и сохраняет `_sat/alley_prev2.jpg`.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146          # горизонт и масштаб: m(y) = K*(y - Y_H) px/м
VANISH = (1035.0, 560.0)       # точка схода (ворота)

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
PROP = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')
os.makedirs(OUT, exist_ok=True)

# --- параметры варианта
Y_GROUND = 900.0      # земля под ближним торцом скамейки
NEAR_X = 210.0        # x ближнего торца
SEAT_ALONG = 0.25     # поэт сидит на 25 % длины от ближнего торца
BENCH_LEN_M, BENCH_BACK_M = 1.8, 0.90

m = K * (Y_GROUND - Y_H)
print('глубина y=%.0f -> масштаб %.0f px/м' % (Y_GROUND, m))
print('скамейка 1.8 м = %.0f px по длине, спинка 0.90 м = %.0f px' % (BENCH_LEN_M * m, BENCH_BACK_M * m))

prop = Image.open(PROP).convert('RGBA')
# спинка в файле занимает 703/986 высоты -> подгоняем высоту файла под нужную спинку
BACK_FRAC = 703.0 / 986.0 * (700.0 / 700.0)
h_px = BENCH_BACK_M * m / (703.0 / 986.0)      # высота файла, при которой спинка = 0.9 м
scale = h_px / prop.height
prop = prop.resize((max(1, round(prop.width * scale)), max(1, round(h_px))), Image.LANCZOS)
print('файл пропа после масштаба: %dx%d' % prop.size)

# земля и линия сиденья в файле (по маске исходника 1303x986: земля y=860, сиденье y=508)
# в vn2/prop/bench.webp (925x700) те же доли: земля 860/986, сиденье 508/986
ground_y_f = prop.height * (860.0 / 986.0)
seat_y_f = prop.height * (508.0 / 986.0)
print('в файле: земля y=%.0f, сиденье y=%.0f (высота %d)' % (ground_y_f, seat_y_f, prop.height))

# --- наклон оси к точке схода
dx, dy = VANISH[0] - NEAR_X, VANISH[1] - Y_GROUND
angle = np.degrees(np.arctan2(-dy, dx))     # вверх-вправо => положительный
print('наклон оси скамейки к точке схода: %.1f°' % angle)

# --- поворот вокруг точки «земля у ближнего торца»
anchor = (0.0, ground_y_f)                  # левый-нижний угол файла
rot = prop.rotate(angle, resample=Image.BICUBIC, expand=True, center=anchor)
# куда уехала точка-якорь после поворота с expand=True
th = np.deg2rad(angle)
# PIL rotate вращает вокруг center=(x,y) внутри исходного; с expand добавляет поля
new_w, new_h = rot.size
# координата якоря в новом холсте: PIL считает её как поворот вокруг центра + сдвиг
cx, cy = prop.width / 2.0, prop.height / 2.0
ax = anchor[0] - cx
ay = anchor[1] - cy
# экранные координаты, y вниз; PIL крутит против часовой в декартовых => в экранных
# точка (ax,ay) -> (ax*cos + ay*sin, -ax*sin + ay*cos)
nx = ax * np.cos(th) + ay * np.sin(th)
ny = -ax * np.sin(th) + ay * np.cos(th)
anchor_x_new = nx + new_w / 2.0
anchor_y_new = ny + new_h / 2.0

# сиденье у ближнего торца в новом холсте
sx, sy = 0.0 - cx, seat_y_f - cy
sx_n = sx * np.cos(th) + sy * np.sin(th) + new_w / 2.0
sy_n = -sx * np.sin(th) + sy * np.cos(th) + new_h / 2.0

# --- сборка
bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')


def place_center_left(canvas, img, left_pct=73.0, bottom_pct=-3.0, height_pct=99.0):
    im = img
    h = round(H * height_pct / 100.0)
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    top = round(H * (1.0 - bottom_pct / 100.0)) - h
    left = round(W * left_pct / 100.0 - w / 2.0)
    canvas.alpha_composite(im, (left, top))
    return (left, top, left + w, top + h)


kate_bb = place_center_left(bg, Image.open(KATE), 73, -3, 99)

# вставляем повёрнутый проп так, чтобы якорь (земля ближнего торца) попал в (NEAR_X,
# Y_GROUND)
dx_paste = int(round(NEAR_X - anchor_x_new))
dy_paste = int(round(Y_GROUND - anchor_y_new))
bg.alpha_composite(rot, (dx_paste, dy_paste))
prop_bb = (dx_paste, dy_paste, dx_paste + rot.width, dy_paste + rot.height)
print('проп на экране bbox', prop_bb, 'размер', rot.size)

# --- поэт: масштаб в ту же глубину, посадка бёдрами на линию сиденья, наклон тот же
FILL, HIP = 0.85, 0.346                 # фигура = 0.85 холста, бёдра 0.346 от ступней
fig_px = 1.30 * m
canvas_px = fig_px / FILL
poet = Image.open(POET).convert('RGBA')
ph = round(canvas_px)
pw = round(poet.width * ph / poet.height)
poet = poet.resize((pw, ph), Image.LANCZOS)

# бёдра в файле поэта: alpha bbox (21,201,556,1419), ступни ~1419
feet_f = 1419.0 / 1433.0 * ph
hip_f = feet_f - HIP * fig_px
print('поэт: холст %dx%d, фигура %.0f px (1.30 м), ступни y=%.0f, бёдра y=%.0f внутри файла'
      % (pw, ph, fig_px, feet_f, hip_f))

# точка посадки на сиденье: 25 % длины от ближнего торца (в экранных координатах)
seat_pt_x = NEAR_X + dx_paste + (sx_n - 0.0)     # не используется напрямую; считаем ниже
# линия сиденья в экране: от ближнего торца (NEAR_X, Y_GROUND - (860-508)/986*h_px) к
# дальнему; проще — берём точку на 25 % вдоль по оси наклона на длине 0.25*1.8 м
along = SEAT_ALONG * BENCH_LEN_M * m
hip_x = NEAR_X + along * np.cos(th)
hip_y = (Y_GROUND - (ground_y_f - seat_y_f)) - along * np.sin(th)
print('посадка: бёдра в экране (%.0f, %.0f)' % (hip_x, hip_y))

# ПОЭТА НЕ НАКЛОНЯЕМ: в перспективе с горизонтальной камерой вертикали остаются
# вертикальными — сидит на наклонной скамейке, но сам стоит прямо.
pr = poet
poet_anchor_x = pw / 2.0
poet_anchor_y = hip_f
px_paste = int(round(hip_x - poet_anchor_x))
py_paste = int(round(hip_y - poet_anchor_y))
bg.alpha_composite(pr, (px_paste, py_paste))
poet_bb = (px_paste, py_paste, px_paste + pr.width, py_paste + pr.height)
print('поэт на экране bbox', poet_bb)

p1 = os.path.join(OUT, 'alley_prev2.jpg')
bg.convert('RGB').save(p1, quality=90)
print('saved', os.path.relpath(p1, HERE), os.path.getsize(p1), 'B')
p2 = os.path.join(OUT, 'alley_prev2_small.jpg')
bg.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p2, quality=88)
print('saved', os.path.relpath(p2, HERE), os.path.getsize(p2), 'B')
