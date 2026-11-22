# -*- coding: utf-8 -*-
"""Посадка скамейки с мягкой контактной тенью и лёгким смягчением краёв.

Геометрия: рендер снят с высоты 1/1.146 м, поэтому масштаб берётся из
m(y) = (y - горизонт)/0.8726 (у кадра и рендера она одна), посадка — сдвиг,
при котором горизонт рендера попадает в горизонт кадра y=572.
"""
import math
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H_SCENE = 572.0
CAMH = 1.0 / 1.146
Y_H_RENDER = 403.42
Y_LEG_SCENE = 960.0
SEAT_H = 0.45
POET_H = 780
P_BUTT_F = 0.625
RESX, RESY = 3000, 1800
LENS, SENSOR = 50.0, 36.0
F = RESX * LENS / SENSOR
CX, CY, CAMZ, TZ = 1.8903, -3.0, CAMH, 0.45
L_B, DEPTH_B = 1.80, 0.56


def proj(p3):
    C = np.array([CX, CY, CAMZ], float)
    fwd = np.array([0.0, 0.0, TZ]) - C
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    d = np.array(p3, float) - C
    x, y, z = d @ right, d @ up, d @ fwd
    return np.array([RESX / 2 + F * x / z, RESY / 2 - F * y / z])
EDGE_BLUR = float(os.environ.get('EDGE_BLUR', '0.9'))
SHADOW_ALPHA = float(os.environ.get('SHADOW_ALPHA', '0.42'))

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
BENCH = os.path.join(ROOT, '_sat', 'blend', os.environ.get('BENCH', 'bench7B.png'))
PREFIX = os.environ.get('PREFIX', 'blend7')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')


def m_scene(y):
    return (y - Y_H_SCENE) / CAMH


def curb(y):
    return 0.2856 * y - 108.5


def main():
    bench = Image.open(BENCH).convert('RGBA')
    al = np.asarray(bench)[:, :, 3]
    h, w = al.shape
    m = al > 140

    bot = np.full(w, -1)
    for x in range(w):
        idx = np.nonzero(m[:, x])[0]
        if idx.size:
            bot[x] = idx.max()
    y_anchor = float(bot.max())
    cols = np.nonzero(bot > y_anchor - 0.02 * h)[0]
    x_anchor = float(cols.mean())
    k_render = (y_anchor - Y_H_RENDER) / CAMH
    s = m_scene(Y_LEG_SCENE) / k_render
    print('опора (%.0f, %.0f), K %.0f px/м, s=%.4f' % (x_anchor, y_anchor, k_render, s))

    bw, bh = max(1, round(w * s)), max(1, round(h * s))
    bs = bench.resize((bw, bh), Image.LANCZOS)
    if EDGE_BLUR > 0:
        rgb = bs.convert('RGB').filter(ImageFilter.GaussianBlur(EDGE_BLUR))
        alpha = bs.split()[3].filter(ImageFilter.GaussianBlur(EDGE_BLUR * 0.9))
        bs = Image.merge('RGBA', (*rgb.split(), alpha))

    arr = np.asarray(bs)[:, :, 3] > 128
    left_local = int(np.nonzero(arr.any(axis=0))[0].min())
    px = int(round(curb(Y_LEG_SCENE) + 15 - left_local))
    py = int(round(Y_LEG_SCENE - y_anchor * s))
    print('вставка (%d, %d), файл %dx%d, левый край %d (бордюр %.0f)'
          % (px, py, bw, bh, px + left_local, curb(Y_LEG_SCENE)))

    canvas = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    kate = Image.open(KATE).convert('RGBA')
    kh = round(H * 0.99)
    kw = round(kate.width * kh / kate.height)
    kate = kate.resize((kw, kh), Image.LANCZOS)
    canvas.alpha_composite(kate, (round(W * 0.73 - kw / 2.0), round(H * 1.03) - kh))

    # контактная тень: силуэт скамейки, приплюснутый и размытый, кладём на землю
    flat = bs.split()[3].resize((bw, max(1, int(bh * 0.16))), Image.LANCZOS)
    flat = flat.filter(ImageFilter.GaussianBlur(max(2, int(14 * s * 6))))
    fw, fh = flat.size
    shadow = Image.new('RGBA', (fw, fh), (32, 40, 34, 0))
    shadow.putalpha(flat.point(lambda v: int(v * SHADOW_ALPHA)))
    base_y = py + int(y_anchor * s)
    canvas.alpha_composite(shadow, (px, base_y - fh // 2))

    canvas.alpha_composite(bs, (px, py))

    seat_local = proj((-0.03, -L_B / 2 + 0.075 + 0.40, SEAT_H))
    seat_x = px + seat_local[0] * s
    seat_y = py + seat_local[1] * s
    poet = Image.open(POET).convert('RGBA')
    pw = round(poet.width * POET_H / poet.height)
    poet = poet.resize((pw, POET_H), Image.LANCZOS)
    canvas.alpha_composite(poet, (int(round(seat_x - pw / 2.0)),
                                  int(round(seat_y - P_BUTT_F * POET_H))))
    print('земля под скамейкой %d, сиденье %.0f, таз поэта %.0f' %
          (base_y, seat_y, seat_y))

    full = canvas.convert('RGB')
    full.save(os.path.join(OUT, PREFIX + '_full.jpg'), quality=90)
    full.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, PREFIX + '.jpg'), quality=88)
    full.crop((0, int(H * 0.34), int(W * 0.62), H)).save(
        os.path.join(OUT, PREFIX + '_crop.jpg'), quality=92)
    print('saved', PREFIX + '*.jpg')


if __name__ == '__main__':
    main()
