# -*- coding: utf-8 -*-
"""Быстрый A/B: та же сцена, но скамейка сдвинута ПРАВЕЕ бордюра (на асфальт).

Привязка: земля у ближней ножки, X_LEG задаётся так, чтобы левый край пропа был правее
линии бордюра на этой глубине (бордюр: x = 0.2856*y - 108.5).

Печатает, где бордюр, где левый край и где ножка — чтобы «на асфальте» было не на слово,
а числом.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

W, H = 1920, 1080
Y_H, K = 572.0, 1.146
VANISH = (1037.0, 572.0)
BACK_H, SEAT_H = 0.90, 0.45
BUTT_FX = 0.295
P_HEAD_F, P_FEET_F, P_BUTT_F = 201 / 1433.0, 1419 / 1433.0, 0.625
POET_H = 780

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

PROPS = {
    'A старая': dict(path=os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png'),
                     leg_x=0.100, leg_y=0.881, top=0.160, seat=0.624, ground=0.986, axis=26.2),
    'B новая': dict(path=os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png'),
                    leg_x=0.0696, leg_y=0.8715, top=0.1295, seat=0.628, ground=0.999, axis=19.6),
}


def curb_x(y):
    return 0.2856 * y - 108.5


def render(cfg, label, y_leg, x_leg):
    m = K * (y_leg - Y_H)
    alley = np.degrees(np.arctan2(y_leg - VANISH[1], VANISH[0] - x_leg))
    prop0 = Image.open(cfg['path']).convert('RGBA')
    h_file = BACK_H * m / (cfg['leg_y'] - cfg['top'])
    prop0 = prop0.resize((max(1, round(prop0.width * h_file / prop0.height)),
                          max(1, round(h_file))), Image.LANCZOS)
    rot = alley - cfg['axis']
    ax, ay = cfg['leg_x'] * prop0.width, cfg['leg_y'] * prop0.height
    prop = prop0.rotate(rot, resample=Image.BICUBIC, expand=True, center=(ax, ay))
    th = np.deg2rad(rot)
    cx, cy = prop0.width / 2.0, prop0.height / 2.0

    def moved(px, py):
        x, y = px - cx, py - cy
        return (x * np.cos(th) + y * np.sin(th) + prop.width / 2.0,
                -x * np.sin(th) + y * np.cos(th) + prop.height / 2.0)

    a_new = moved(ax, ay)
    paste = (int(round(x_leg - a_new[0])), int(round(y_leg - a_new[1])))
    seat_pt = moved(BUTT_FX * prop0.width, cfg['seat'] * prop0.height)
    seat = (paste[0] + seat_pt[0], paste[1] + seat_pt[1])

    canvas = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    def put(c, p, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
        i2 = Image.open(p).convert('RGBA')
        h = round(H * height_pct / 100.0)
        w = round(i2.width * h / i2.height)
        i2 = i2.resize((w, h), Image.LANCZOS)
        c.alpha_composite(i2, (round(W * left_pct / 100.0 - w / 2.0),
                               round(H * (1.0 - bottom_pct / 100.0)) - h))

    put(canvas, KATE, 73, 99, -3)
    canvas.alpha_composite(prop, paste)
    poet = Image.open(POET).convert('RGBA')
    pw = round(poet.width * POET_H / poet.height)
    poet = poet.resize((pw, POET_H), Image.LANCZOS)
    px = int(round(seat[0] - pw / 2.0))
    py = int(round(seat[1] - P_BUTT_F * POET_H))
    canvas.alpha_composite(poet, (px, py))

    print('%s: X_LEG=%.0f Y_LEG=%.0f | бордюр x=%.0f, левый край пропа x=%d, ножка x=%.0f, '
          'сиденье (%.0f,%.0f), поэт x %d..%d'
          % (label, x_leg, y_leg, curb_x(y_leg), paste[0], x_leg, seat[0], seat[1], px, px + pw))
    return canvas, paste[0], seat


def solve_x(cfg, y_leg, inset=10.0):
    """Какой X_LEG нужен, чтобы ЛЕВЫЙ край пропа встал правее бордюра на inset px."""
    canvas, left, _ = render(cfg, 'probe', y_leg, 300.0)
    return 300.0 + (curb_x(y_leg) + inset - left)


def main():
    y = float(os.environ.get('Y_LEG', 960))
    auto = os.environ.get('AUTO', '1') != '0'
    x_fixed = float(os.environ.get('X_LEG', 210))
    frames = []
    for lab, cfg in PROPS.items():
        x = solve_x(cfg, y) if auto else x_fixed
        canvas, left, seat = render(cfg, lab, y, x)
        frames.append((lab, canvas, x, left))
    labs = [f[0] for f in frames]
    box = (0, int(H * 0.33), int(W * 0.60), H)
    crops = [f[1].convert('RGB').crop(box) for f in frames]
    cw, ch = crops[0].size
    sh = Image.new('RGB', (cw * 2, ch), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for i, (lab, _, x, left) in enumerate(zip(labs, [f[1] for f in frames],
                                             [f[2] for f in frames],
                                             [f[3] for f in frames])):
        sh.paste(crops[i], (cw * i, 0))
        d.rectangle([cw * i + 10, 10, cw * i + 430, 56], fill=(255, 255, 255))
        d.text((cw * i + 20, 26), '%s  X=%.0f (край %d, бордюр %.0f)'
               % (lab, x, left, curb_x(y)), fill=(170, 0, 0))
    p = os.path.join(OUT, 'AB_on_asphalt.jpg')
    sh.save(p, quality=90)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')


if __name__ == '__main__':
    main()
