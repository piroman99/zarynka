# -*- coding: utf-8 -*-
"""Посадка блендер-скамейки в кадр «аллея» по перспективе кадра.

Рендер снят камерой, у которой высота = 1/1.146 м (ровно как у кадра), поэтому
земля рендера и земля кадра совпадают: масштаб = m_сцена(y)/m_рендер(y).
Опорная точка — контакт передней ближней ножки с землёй; по X сдвигаем так,
чтобы левый край маски был на 15 px правее линии бордюра.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H_SCENE, K_SCENE = 572.0, 1.146
Y_H_RENDER, CAMH = 403.42, 1.0 / 1.146
RESX, RESY = 3000, 1800
LENS, SENSOR = 50.0, 36.0
CX, CY, CAMZ, TZ = 1.8903, -3.0, CAMH, 0.45
F = RESX * LENS / SENSOR
Y_LEG_SCENE = 960.0
SEAT_H = 0.45
POET_H = 780
P_BUTT_F = 0.625

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
BENCH = os.path.join(ROOT, '_sat', 'blend', 'bench5.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')


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


def m_scene(y):
    return K_SCENE * (y - Y_H_SCENE)


def m_render(y):
    return (y - Y_H_RENDER) / CAMH


def curb(y):
    return 0.2856 * y - 108.5


def main():
    bench = Image.open(BENCH).convert('RGBA')
    a = np.asarray(bench)[:, :, 3]
    h, w = a.shape
    m = a > 140

    # опора: нижняя полоса маски (передняя ближняя ножка)
    bot = np.full(w, -1)
    for x in range(w):
        idx = np.nonzero(m[:, x])[0]
        if idx.size:
            bot[x] = idx.max()
    y_bot = bot.max()
    cols = np.nonzero(bot > y_bot - 0.02 * h)[0]
    x_anchor = float(cols.mean())
    y_anchor = float(y_bot)
    print('опора рендера: (%.1f, %.1f); K_рендер = %.1f px/м'
          % (x_anchor, y_anchor, m_render(y_anchor)))

    s = m_scene(Y_LEG_SCENE) / m_render(y_anchor)
    print('масштаб s = %.4f (сцена %.1f px/м при y=%.0f)' % (s, m_scene(Y_LEG_SCENE), Y_LEG_SCENE))

    bw, bh = int(round(w * s)), int(round(h * s))
    bs = bench.resize((bw, bh), Image.LANCZOS)
    # куда ставим: опора рендера -> (x, y)
    x0 = float(cols.min()) * s
    best = None
    for x_try in range(-400, 1900, 4):
        left = None
        px = int(round(x_try - x_anchor * s))
        py = int(round(Y_LEG_SCENE - y_anchor * s))
        arr = np.asarray(bs)[:, :, 3] > 140
        colsum = arr.any(axis=0)
        lx = int(np.nonzero(colsum)[0].min()) + px
        if left is None:
            left = lx
        if abs(left - (curb(Y_LEG_SCENE) + 15)) <= 2:
            best = (px, py, left)
            break
    if best is None:
        px = int(round(curb(Y_LEG_SCENE) + 15 - x0 - 0))
        py = int(round(Y_LEG_SCENE - y_anchor * s))
        arr = np.asarray(bs)[:, :, 3] > 140
        px = int(round(curb(Y_LEG_SCENE) + 15 - (int(np.nonzero(arr.any(axis=0))[0].min()))))
        best = (px, py, curb(Y_LEG_SCENE) + 15)
    px, py, left = best
    print('вставка в (%.0f, %.0f), левый край %d (бордюр %.0f), файл %dx%d'
          % (px, py, left, curb(Y_LEG_SCENE), bw, bh))

    canvas = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    kate = Image.open(KATE).convert('RGBA')
    kh = round(H * 0.99)
    kw = round(kate.width * kh / kate.height)
    kate = kate.resize((kw, kh), Image.LANCZOS)
    canvas.alpha_composite(kate, (round(W * 0.73 - kw / 2.0), round(H * 1.03) - kh))

    canvas.alpha_composite(bs, (px, py))

    # поэт: таз на сиденье, 0.42 м от ближнего торца
    seat_r = proj((-0.02, -0.90 + 0.42, SEAT_H))
    seat_s = (seat_r[0] * s + px, seat_r[1] * s + py)
    poet = Image.open(POET).convert('RGBA')
    pw = round(poet.width * POET_H / poet.height)
    poet = poet.resize((pw, POET_H), Image.LANCZOS)
    canvas.alpha_composite(poet, (int(round(seat_s[0] - pw / 2.0)),
                                  int(round(seat_s[1] - P_BUTT_F * POET_H))))
    print('сиденье поэта в кадре: (%.0f, %.0f), земля там %.0f, высота сиденья %.0f px'
          % (seat_s[0], seat_s[1], seat_s[1] + SEAT_H * m_scene(seat_s[1]),
             SEAT_H * m_scene(seat_s[1])))

    full = canvas.convert('RGB')
    full.save(os.path.join(OUT, 'blend_bench_full.jpg'), quality=90)
    full.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, 'blend_bench.jpg'), quality=88)

    crop = full.crop((0, int(H * 0.34), int(W * 0.62), H))
    crop.save(os.path.join(OUT, 'blend_bench_crop.jpg'), quality=92)
    print('saved blend_bench*.jpg', crop.size)


if __name__ == '__main__':
    main()
