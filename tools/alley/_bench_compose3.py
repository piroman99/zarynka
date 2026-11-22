# -*- coding: utf-8 -*-
"""Посадка ГОТОВОГО пропа (уже в конечном масштабе) в кадр «аллея».

Проп задаётся env PROP=<path RGBA>. Ставится так, что низ силуэта ложится на
землю y=960 (пиксели кадра), левый край — на curb(960)+15 = 181.
Тень, поэт и Екатерина — как в _bench_compose2.py.
"""
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W, H = 1920, 1080
Y_H_SCENE = 572.0
CAMH = 1.0 / 1.146
Y_GROUND = 960.0
SEAT_H = 0.45
POET_H = 780
P_BUTT_F = 0.625
RESX, RESY = 3000, 1800
LENS, SENSOR = 50.0, 36.0
F = RESX * LENS / SENSOR
CX, CY, CAMZ, TZ = 1.8903, -3.0, CAMH, 0.45
L_B = 1.80

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

PROP = os.path.join(ROOT, '_sat', 'wc', os.environ.get('PROP', 'prop_A.png'))
PREFIX = os.environ.get('PREFIX', 'wc_A')


def m_scene(y):
    return (y - Y_H_SCENE) / CAMH


def curb(y):
    return 0.2856 * y - 108.5


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


def main():
    prop = Image.open(PROP).convert('RGBA')
    a = np.asarray(prop)[:, :, 3]
    m = a > 60
    rows = np.nonzero(m.any(axis=1))[0]
    cols = np.nonzero(m.any(axis=0))[0]
    y_bot, x_left = int(rows.max()), int(cols.min())
    px = int(round(curb(Y_GROUND) + 15 - x_left))
    py = int(round(Y_GROUND - y_bot))
    print('%s: %dx%d, силуэт y до %d, левый x %d -> вставка (%d, %d), левый край %d'
          % (os.path.basename(PROP), prop.width, prop.height, y_bot, x_left, px, py, px + x_left))

    canvas = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    kate = Image.open(KATE).convert('RGBA')
    kh = round(H * 0.99)
    kw = round(kate.width * kh / kate.height)
    kate = kate.resize((kw, kh), Image.LANCZOS)
    canvas.alpha_composite(kate, (round(W * 0.73 - kw / 2.0), round(H * 1.03) - kh))

    # контактная тень под скамейкой
    flat = prop.split()[3].resize((prop.width, max(1, int(prop.height * 0.16))), Image.LANCZOS)
    flat = flat.filter(ImageFilter.GaussianBlur(9))
    shadow = Image.new('RGBA', flat.size, (34, 42, 36, 0))
    shadow.putalpha(flat.point(lambda v: int(v * 0.42)))
    canvas.alpha_composite(shadow, (px, py + y_bot - flat.size[1] // 2))

    canvas.alpha_composite(prop, (px, py))

    # поэт: таз на доске
    s = prop.width / 876.0
    seat_local = proj((-0.03, -L_B / 2 + 0.075 + 0.40, SEAT_H))
    seat_x = px + seat_local[0] * 0.29200 * s
    seat_y = py + seat_local[1] * 0.29200 * s
    poet = Image.open(POET).convert('RGBA')
    pw = round(poet.width * POET_H / poet.height)
    poet = poet.resize((pw, POET_H), Image.LANCZOS)
    canvas.alpha_composite(poet, (int(round(seat_x - pw / 2.0)),
                                  int(round(seat_y - P_BUTT_F * POET_H))))
    print('  таз поэта (%.0f, %.0f), земля под скамейкой %d' % (seat_x, seat_y,
                                                                py + y_bot))

    full = canvas.convert('RGB')
    full.save(os.path.join(OUT, PREFIX + '_full.jpg'), quality=90)
    full.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, PREFIX + '.jpg'), quality=88)
    full.crop((60, 400, 800, 1000)).save(os.path.join(OUT, PREFIX + '_bench.jpg'), quality=93)
    z = full.crop((150, 560, 640, 900))
    z = z.resize((int(z.width * 2.0), int(z.height * 2.0)), Image.LANCZOS)
    z.save(os.path.join(OUT, PREFIX + '_bench_zoom.jpg'), quality=94)
    print('  saved', PREFIX + '*.jpg')


if __name__ == '__main__':
    main()
