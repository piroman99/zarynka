# -*- coding: utf-8 -*-
"""v9: скамейка ещё левее; поэт крупнее, посадка по ВИДИМОЙ линии таза.

Почему v8 «завис»: линию таза я брал как 0.346 высоты фигуры от ступней (=0.696 доли
файла), но у нарисованной фигуры это геометрическая середина бёдер, а не точка касания
сиденья. Замер маски (`_poet_profile.py`): фигура y 201..1418, ноги разделяются на два
сегмента начиная с доли 0.57 фигуры → это и есть линия таза/промежности:
  0.140 + 0.57*0.85 = 0.625 доли файла.
При посадке по 0.696 фигура оказывается на 0.071*683 = 48 px (11 см) ВЫШЕ сиденья —
ровно то, что видно как «висит».

Второе: ступни не обязаны попадать на ту же строку, что земля у скамейки. Скамейка
стоит глубже в кадре, поэт ближе к камере, поэтому его земля законно ниже. Отсюда
можно сделать его крупнее, не отрывая таз от доски.

Крутилки: X_LEG (положение скамейки), PH_LIST (высоты спрайта для листа).
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146
VANISH = (1037.0, 572.0)

Y_LEG = float(os.environ.get('Y_LEG', 960))
X_LEG = float(os.environ.get('X_LEG', 148))
LEG_X_F, LEG_Y_F = 0.10, 0.881
BACK_TOP_F = 0.160
SEAT_F, GROUND_F = 0.624, 0.986
BUTT_FX = 0.295
BACK_H = 0.90

P_HEAD_F, P_FEET_F = 201.0 / 1433.0, 1419.0 / 1433.0
P_BUTT_F = 0.625                      # видимая линия таза (замер по маске)

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
seat_x, seat_y = paste[0] + seat_pt[0], paste[1] + seat_pt[1]
bench_ground = paste[1] + moved(BUTT_FX * prop0.width, GROUND_F * prop0.height)[1]
print('скамейка x=%0.f: вставка (%d,%d), поворот %.1f°' % (X_LEG, paste[0], paste[1], ROT))
print('сиденье у поэта (%.0f, %.0f), земля скамейки y=%.0f, %.0f px/м'
      % (seat_x, seat_y, bench_ground, m))

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
base = bg.copy()


def render(ph):
    canvas = base.copy()
    poet = Image.open(POET).convert('RGBA')
    pw = round(poet.width * ph / poet.height)
    poet = poet.resize((pw, max(1, int(ph))), Image.LANCZOS)
    ph2 = poet.height
    px = int(round(seat_x - pw / 2.0))
    py = int(round(seat_y - P_BUTT_F * ph2))
    canvas.alpha_composite(poet, (px, py))
    feet = py + P_FEET_F * ph2
    fig = (P_FEET_F - P_HEAD_F) * ph2
    print('  спрайт %d px: фигура %.0f px = %.2f м, ступни y=%.0f (земля скамейки %.0f, '
          'на %.0f px ниже — поэт ближе к камере), таз %+.0f px'
          % (ph2, fig, fig / m, feet, bench_ground, feet - bench_ground,
             py + P_BUTT_F * ph2 - seat_y))
    return canvas


SIZES = [780, 810, 840]
imgs = [render(s) for s in SIZES]

p1 = os.path.join(OUT, 'alley_prev9.jpg')
imgs[1].convert('RGB').resize((1280, 720), Image.LANCZOS).save(p1, quality=88)
imgs[1].convert('RGB').save(os.path.join(OUT, 'alley_prev9_full.jpg'), quality=90)
print('saved', os.path.relpath(p1, HERE), os.path.getsize(p1), 'B')

# лист для проверки моделью: три размера, кроп вокруг скамейки
crop_box = (0, int(H * 0.30), int(W * 0.55), H)
crops = []
for im in imgs:
    c = im.convert('RGB').crop(crop_box)
    crops.append(c)
cw, ch = crops[0].size
sheet = Image.new('RGB', (cw * 3, ch), (250, 250, 250))
d = ImageDraw.Draw(sheet)
for i, c in enumerate(crops):
    sheet.paste(c, (cw * i, 0))
    d.rectangle([cw * i + 8, 8, cw * i + 78, 56], fill=(255, 255, 255))
    d.text((cw * i + 24, 20), 'ABC'[i], fill=(200, 0, 0))
ps = os.path.join(OUT, 'v9_sheet.jpg')
sheet.save(ps, quality=86)
print('saved', os.path.relpath(ps, HERE), sheet.size, os.path.getsize(ps), 'B')
