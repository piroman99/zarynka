# -*- coding: utf-8 -*-
"""A/B одной сцены: твоя скамейка против новой, при ОДИНАКОВОМ масштабе и посадке.

Обе ставятся по правилам принятого v9 (который ты одобрил):
  • высота ближнего торца (верх спинки -> земля) = 0.90 м = 400 px при 445 px/м;
  • земля у ближней ножки в одной и той же точке (X_LEG=148, Y_LEG=960);
  • сиденье 0.45 м над землёй, поэт тазом на нём, спрайт 780 px, x = 29.5 % длины.

Отличается ТОЛЬКО рисунок скамейки. Запуск: python3 _bench_ab.py
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
BACK_H, SEAT_H = 0.90, 0.45
BUTT_FX = 0.295
P_HEAD_F, P_FEET_F, P_BUTT_F = 201 / 1433.0, 1419 / 1433.0, 0.625
POET_H = 780

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

# рамки каждого пропа: доли файла (замеры масками)
PROPS = {
    'A старая': dict(path=os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png'),
                     leg_x=0.100, leg_y=0.881, top=0.160, seat=0.624, ground=0.986, axis=26.2),
    'B новая': dict(path=os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png'),
                    leg_x=0.0696, leg_y=0.8715, top=0.1295, seat=0.628, ground=0.999, axis=19.6),
}

m = K * (Y_LEG - Y_H)
alley_deg = np.degrees(np.arctan2(Y_LEG - VANISH[1], VANISH[0] - X_LEG))


def render(cfg, label):
    prop0 = Image.open(cfg['path']).convert('RGBA')
    h_file = BACK_H * m / (cfg['leg_y'] - cfg['top'])
    prop0 = prop0.resize((max(1, round(prop0.width * h_file / prop0.height)),
                          max(1, round(h_file))), Image.LANCZOS)
    rot = alley_deg - cfg['axis']
    ax, ay = cfg['leg_x'] * prop0.width, cfg['leg_y'] * prop0.height
    prop = prop0.rotate(rot, resample=Image.BICUBIC, expand=True, center=(ax, ay))
    th = np.deg2rad(rot)
    cx, cy = prop0.width / 2.0, prop0.height / 2.0

    def moved(px, py):
        x, y = px - cx, py - cy
        return (x * np.cos(th) + y * np.sin(th) + prop.width / 2.0,
                -x * np.sin(th) + y * np.cos(th) + prop.height / 2.0)

    a_new = moved(ax, ay)
    paste = (int(round(X_LEG - a_new[0])), int(round(Y_LEG - a_new[1])))
    seat_pt = moved(BUTT_FX * prop0.width, cfg['seat'] * prop0.height)
    seat = (paste[0] + seat_pt[0], paste[1] + seat_pt[1])
    gnd_pt = moved(BUTT_FX * prop0.width, cfg['ground'] * prop0.height)
    ground_at_poet = paste[1] + gnd_pt[1]

    bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    def put(canvas, p, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
        i2 = Image.open(p).convert('RGBA')
        h = round(H * height_pct / 100.0)
        w = round(i2.width * h / i2.height)
        i2 = i2.resize((w, h), Image.LANCZOS)
        canvas.alpha_composite(i2, (round(W * left_pct / 100.0 - w / 2.0),
                                    round(H * (1.0 - bottom_pct / 100.0)) - h))

    put(bg, KATE, 73, 99, -3)
    bg.alpha_composite(prop, paste)

    poet = Image.open(POET).convert('RGBA')
    pw = round(poet.width * POET_H / poet.height)
    poet = poet.resize((pw, POET_H), Image.LANCZOS)
    px = int(round(seat[0] - pw / 2.0))
    py = int(round(seat[1] - P_BUTT_F * POET_H))
    bg.alpha_composite(poet, (px, py))

    print('%s: h_file %.0f, поворот %+.1f°, bbox (%d,%d)-(%d,%d)'
          % (label, h_file, rot, paste[0], paste[1], paste[0] + prop.width, paste[1] + prop.height))
    print('   земля у ближней ножки (%.0f,%.0f); сиденье у поэта (%.0f,%.0f); земля там y=%.0f'
          % (X_LEG, Y_LEG, seat[0], seat[1], ground_at_poet))
    print('   поэт %d px в (%d,%d): таз %+.0f px, ступни y=%.0f (низ кадра %d)'
          % (POET_H, px, py, py + P_BUTT_F * POET_H - seat[1],
             py + P_FEET_F * POET_H, H))
    print('   левый край пропа x=%d (бордюр на этой глубине ~%.0f)'
          % (paste[0], 0.2856 * Y_LEG - 108.5))
    return bg


def main():
    frames = {lab: render(cfg, lab) for lab, cfg in PROPS.items()}
    labs = list(frames)

    full = [frames[l].convert('RGB').resize((1280, 720), Image.LANCZOS) for l in labs]
    sh = Image.new('RGB', (2560, 720), (255, 255, 255))
    d = ImageDraw.Draw(sh)
    for i, (l, f) in enumerate(zip(labs, full)):
        sh.paste(f, (1280 * i, 0))
        d.rectangle([1280 * i + 12, 12, 1280 * i + 300, 56], fill=(255, 255, 255))
        d.text((1280 * i + 22, 26), l, fill=(170, 0, 0))
    p1 = os.path.join(OUT, 'AB_full.jpg')
    sh.save(p1, quality=88)
    print('saved', os.path.relpath(p1, HERE), sh.size, os.path.getsize(p1), 'B')

    box = (0, int(H * 0.33), int(W * 0.56), H)
    crops = [frames[l].convert('RGB').crop(box) for l in labs]
    cw, ch = crops[0].size
    sh2 = Image.new('RGB', (cw * 2, ch), (255, 255, 255))
    d2 = ImageDraw.Draw(sh2)
    for i, (l, c) in enumerate(zip(labs, crops)):
        sh2.paste(c, (cw * i, 0))
        d2.rectangle([cw * i + 10, 10, cw * i + 260, 54], fill=(255, 255, 255))
        d2.text((cw * i + 20, 24), l, fill=(170, 0, 0))
    p2 = os.path.join(OUT, 'AB_bench.jpg')
    sh2.save(p2, quality=90)
    print('saved', os.path.relpath(p2, HERE), sh2.size, os.path.getsize(p2), 'B')


if __name__ == '__main__':
    main()
