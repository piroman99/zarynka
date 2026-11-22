# -*- coding: utf-8 -*-
"""Лист вариантов посадки поэта на скамейку — чтобы выбрать числами и глазами модели.

Скамейка одна и та же (положение по слову Ивана: чуть правее и ниже, задняя левая ножка
у бордюра на асфальте). Меняется только поэт: высота спрайта и куда садится таз.

Модель со зрением получает лист с подписями A/B/C/D и говорит, какой вариант правильный
и что не так в остальных. Своего зрения у меня нет, а тыкать наугад в Ивана не хочу.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(os.path.dirname(HERE))
W, H = 1920, 1080
Y_H, K = 572.0, 1.146
AXIS = np.deg2rad(26.2)
SEAT_H, BACK_H = 0.45, 0.90

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
PROP = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

Y_LEG = float(os.environ.get('Y_LEG', 960))
X_LEG = float(os.environ.get('X_LEG', 186))
LEG_X_F, LEG_Y_F = 0.10, 0.881
BACK_TOP_F = 0.160
P_SEAT_F, P_FEET_F = 0.595, 0.985
ALONG_M = 0.504

m = K * (Y_LEG - Y_H)
h_file = BACK_H * m / (LEG_Y_F - BACK_TOP_F)
prop = Image.open(PROP).convert('RGBA')
prop = prop.resize((max(1, round(prop.width * h_file / prop.height)), max(1, round(h_file))),
                   Image.LANCZOS)
paste_x = int(round(X_LEG - LEG_X_F * prop.width))
paste_y = int(round(Y_LEG - LEG_Y_F * prop.height))

base = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')


def put_center_left(canvas, path, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
    im = Image.open(path).convert('RGBA')
    h = round(H * height_pct / 100.0)
    w = round(im.width * h / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    top = round(H * (1.0 - bottom_pct / 100.0)) - h
    left = round(W * left_pct / 100.0 - w / 2.0)
    canvas.alpha_composite(im, (left, top))


put_center_left(base, KATE, 73, 99, -3)
base.alpha_composite(prop, (paste_x, paste_y))

seat0 = (X_LEG, Y_LEG - SEAT_H * m)
along_px = ALONG_M * m
seat_x = seat0[0] + along_px * np.cos(AXIS)
seat_y = seat0[1] - along_px * np.sin(AXIS)
print('скамейка: (%d,%d), сиденье над ножкой (%.0f,%.0f), у поэта (%.0f,%.0f)'
      % (paste_x, paste_y, seat0[0], seat0[1], seat_x, seat_y))

# варианты: (имя, высота спрайта px, y таза) — таз явно задаём, чтобы видеть разницу
VARIANTS = [
    ('A', 513, seat_y),          # v5: масштаб из «таз-ступни = высота сиденья»
    ('B', 620, seat_y),          # крупнее, таз там же (ступни утонут)
    ('C', 513, seat_y + 80),     # таз ниже расчётного
    ('D', 620, seat_y + 80),     # крупнее и ниже
]

sheet = Image.new('RGB', (W, H), (255, 255, 255))
draw = ImageDraw.Draw(sheet)
cells = []
for i, (name, ph, butt_y) in enumerate(VARIANTS):
    canvas = base.copy()
    poet = Image.open(POET).convert('RGBA')
    pw = round(poet.width * ph / poet.height)
    poet = poet.resize((pw, ph), Image.LANCZOS)
    px = int(round(seat_x - pw / 2.0))
    py = int(round(butt_y - P_SEAT_F * ph))
    canvas.alpha_composite(poet, (px, py))
    crop = canvas.convert('RGB').crop((0, int(H * 0.25), int(W * 0.62), H))
    crop = crop.resize((int(crop.width * 1.15), int(crop.height * 1.15)), Image.LANCZOS)
    cells.append((name, crop, ph, butt_y, py + P_FEET_F * ph))

cw = cells[0][1].width
ch = cells[0][1].height
sheet = Image.new('RGB', (cw * 2, ch * 2), (250, 250, 250))
draw = ImageDraw.Draw(sheet)
for i, (name, crop, ph, butt_y, feet_y) in enumerate(cells):
    x = (i % 2) * cw
    y = (i // 2) * ch
    sheet.paste(crop, (x, y))
    draw.rectangle([x, y, x + 70, y + 46], fill=(255, 255, 255))
    draw.text((x + 18, y + 12), name, fill=(200, 0, 0))
    print('  %s: спрайт %d px, таз y=%.0f, ступни y=%.0f' % (name, ph, butt_y, feet_y))

p = os.path.join(OUT, 'seat_sheet.jpg')
sheet.save(p, quality=88)
print('saved', os.path.relpath(p, HERE), sheet.size, os.path.getsize(p), 'B')
