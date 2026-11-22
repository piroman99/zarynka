# -*- coding: utf-8 -*-
"""Посадка поэта с масштабом от НОГ, а не от «земли под сиденьем».

Ключевая поправка: ноги сидящего свисают ПЕРЕД скамейкой, то есть ближе к
зрителю, поэтому их земля на экране НИЖЕ контакта передних ножек скамейки.
Значит низ спрайта обязан быть ниже 960 — иначе ноги «стоят» на уровне ножек,
чего в жизни не бывает.

Задаём H_MULT (множитель к предыдущей высоте 518 px) и проверяем:
  * таз на доске (f_seat = 0.6148 -> y_doska),
  * низ спрайта ниже контакта передних ножек (960),
  * рост сидящего в метрах считается по масштабу у ног.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W, H_IMG = 1920, 1080
Y_H, K = 572.0, 1.146
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')
PROP = os.path.join(ROOT, '_sat', 'wc', os.environ.get('PROP', 'prop_B.png'))

H_BASE = 517.73          # высота спрайта из _poet_measure.py
F_SEAT, F_FEET, F_TOP = 0.6148, 0.9895, 0.140
BENCH_FRONT_LEG_GROUND = 960.0

with open(os.path.join(OUT, 'poet_params.json')) as f:
    P = json.load(f)

SEAT_Y = P['seat_frame']       # 711
PX, PY = P['px'], P['py']


def build(h_mult, prefix, guides=False):
    h_px = H_BASE * h_mult
    feet_y = SEAT_Y + (F_FEET - F_SEAT) * h_px
    top_y = feet_y - (F_FEET - F_TOP) * h_px
    fig_px = (F_FEET - F_TOP) * h_px
    m_feet = K * (feet_y - Y_H)
    fig_m = fig_px / m_feet
    print('H_MULT=%.2f: H=%.0f px, низ %.0f, верх %.0f, фигура %.0f px = %.2f м (м %.0f px/м)'
          % (h_mult, h_px, feet_y, top_y, fig_px, fig_m, m_feet))
    print('   низ спрайта %.0f против контакта передних ножек %.0f -> %s (%+.0f px)'
          % (feet_y, BENCH_FRONT_LEG_GROUND,
             'ниже, как надо' if feet_y > BENCH_FRONT_LEG_GROUND else 'ВЫШЕ — плохо',
             feet_y - BENCH_FRONT_LEG_GROUND))

    prop = Image.open(PROP).convert('RGBA')
    canvas = Image.open(BG).convert('RGB').resize((W, H_IMG), Image.LANCZOS).convert('RGBA')

    kate = Image.open(KATE).convert('RGBA')
    kh = round(H_IMG * 0.99)
    kw = round(kate.width * kh / kate.height)
    kate = kate.resize((kw, kh), Image.LANCZOS)
    canvas.alpha_composite(kate, (round(W * 0.73 - kw / 2.0), round(H_IMG * 1.03) - kh))

    pa = np.asarray(prop)[:, :, 3]
    rows = np.nonzero((pa > 60).any(axis=1))[0]
    flat = prop.split()[3].resize((prop.width, max(1, int(prop.height * 0.16))),
                                  Image.LANCZOS).filter(ImageFilter.GaussianBlur(9))
    shadow = Image.new('RGBA', flat.size, (34, 42, 36, 0))
    shadow.putalpha(flat.point(lambda v: int(v * 0.42)))
    canvas.alpha_composite(shadow, (PX, PY + rows.max() - flat.size[1] // 2))
    canvas.alpha_composite(prop, (PX, PY))

    poet = Image.open(POET).convert('RGBA')
    hh = int(round(h_px))
    ww = max(1, round(poet.width * hh / poet.height))
    poet = poet.resize((ww, hh), Image.LANCZOS)
    pl = P['x_poet'] - ww // 2
    pt = int(round(SEAT_Y - F_SEAT * hh))
    canvas.alpha_composite(poet, (pl, pt))

    # проверка контактов по пикселям
    pm = np.zeros((H_IMG, W), bool)
    pm[pt:pt + poet.height, pl:pl + poet.width] = np.asarray(poet)[:, :, 3] > 60
    bm = np.zeros((H_IMG, W), bool)
    bm[PY:PY + prop.height, PX:PX + prop.width] = pa > 60
    inter = (pm & bm).sum()
    bottom = np.nonzero(pm.any(axis=1))[0].max()
    seat_row = np.abs(np.arange(H_IMG) - SEAT_Y) <= 3
    on_seat = (pm & seat_row[:, None]).sum()
    print('   таз на линии доски: %d px, пересечение со скамейкой %d px, низ %d'
          % (on_seat, inter, bottom))

    if guides:
        d = ImageDraw.Draw(canvas)
        d.line([(0, SEAT_Y), (W, SEAT_Y)], fill=(255, 0, 200), width=3)
        d.line([(0, BENCH_FRONT_LEG_GROUND), (W, BENCH_FRONT_LEG_GROUND)],
               fill=(0, 200, 255), width=3)
        d.line([(0, bottom), (W, bottom)], fill=(255, 160, 0), width=3)

    full = canvas.convert('RGB')
    full.save(os.path.join(OUT, prefix + '_full.jpg'), quality=90)
    full.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, prefix + '.jpg'), quality=88)
    full.crop((110, 180, 830, 1080)).save(os.path.join(OUT, prefix + '_zoom.jpg'), quality=94)
    return dict(h_px=h_px, feet=feet_y, top=top_y, fig_m=fig_m, mult=h_mult)


if __name__ == '__main__':
    res = []
    for mult, name in ((1.50, 'sc150'), (1.60, 'sc160')):
        print('--- %s' % name)
        res.append((name, build(mult, name, guides=(name == 'sc150'))))
    with open(os.path.join(OUT, 'poet_scale.json'), 'w') as f:
        json.dump(res, f, indent=2)
