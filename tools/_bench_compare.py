# -*- coding: utf-8 -*-
"""Две скамейки рядом: (A) твоя старая, (B) новая — при ОДИНАКОВОЙ геометрии.

Почему так: в v10 я привязал новую скамейку по земле у ЗАДНЕЙ ножки (y=960), а у старой
привязка шла по земле у ПЕРЕДНЕЙ (y=1025). Из-за этого новая встала глубже и выше, поэт
поднялся на 139 px («взлетел»), а сама скамейка вышла крупнее и полезла на бордюр.

Здесь обе ставятся по одному правилу, взятому из принятого v9:
  • масштаб: высота ближнего торца (верх спинки -> земля у передней ножки) = 0.90 м;
  • привязка: САМАЯ НИЖНЯЯ точка маски пропа ставится в одну и ту же точку экрана;
  • сиденье = эта земля минус 0.45 м; поэт сажается тазом на него, x = 29.5 % длины.
Меняется только сам рисунок скамейки.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146
VANISH = (1037.0, 572.0)

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
OLD = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')
NEW = os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

BACK_H, SEAT_H = 0.90, 0.45
P_HEAD_F, P_FEET_F, P_BUTT_F = 201 / 1433.0, 1419 / 1433.0, 0.625

# общая привязка (из принятого v9)
GROUND_X, GROUND_Y = 379.0, 1015.0     # самая нижняя точка маски старого пропа
X_LEG = 148.0


def load(path):
    im = Image.open(path).convert('RGBA')
    a = np.asarray(im)
    m = a[:, :, 3] > 140
    ys, xs = np.nonzero(m)
    return im, m, int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())


def build(path, label):
    im, m, x0, x1, y0, y1 = load(path)
    Wf, Hf = im.size
    # земля у передней ножки = самая нижняя точка маски
    ybot = y1
    xs_bot = np.nonzero(m[ybot])[0]
    xbot = int(xs_bot.mean())
    # верх ближнего торца: верх маски в левой четверти
    left = np.nonzero(m[:, :int(Wf * 0.30)].any(axis=1))[0]
    ytop_near = int(left.min())
    span_f = (ybot - ytop_near) / Hf
    m_scene = K * (GROUND_Y - Y_H)
    k = (BACK_H * m_scene) / (span_f * Hf)
    prop = im.resize((max(1, round(Wf * k)), max(1, round(Hf * k))), Image.LANCZOS)
    px = int(round(GROUND_X - xbot * k))
    py = int(round(GROUND_Y - ybot * k))
    print('%s: файл %dx%d, земля (%.3f,%.3f), верх торца %.3f -> k=%.3f, проп %dx%d в (%d,%d)'
          % (label, Wf, Hf, xbot / Wf, ybot / Hf, ytop_near / Hf, k, prop.width, prop.height, px, py))
    print('   ближний торец на экране %.0f px = %.2f м; левый край на x=%d'
          % (span_f * Hf * k, span_f * Hf * k / m_scene, px))

    bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    def put(canvas, p, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
        i2 = Image.open(p).convert('RGBA')
        h = round(H * height_pct / 100.0)
        w = round(i2.width * h / i2.height)
        i2 = i2.resize((w, h), Image.LANCZOS)
        canvas.alpha_composite(i2, (round(W * left_pct / 100.0 - w / 2.0),
                                    round(H * (1.0 - bottom_pct / 100.0)) - h))

    put(bg, KATE, 73, 99, -3)
    bg.alpha_composite(prop, (px, py))

    seat = (GROUND_X + (prop.width * 0.295), GROUND_Y - SEAT_H * m_scene)
    poet = Image.open(POET).convert('RGBA')
    ph = int(round((SEAT_H * m_scene) / ((P_FEET_F - P_BUTT_F) * 1.0)))
    ph = 780
    pw = round(poet.width * ph / poet.height)
    poet = poet.resize((pw, ph), Image.LANCZOS)
    ax = int(round(seat[0] - pw / 2.0))
    ay = int(round(seat[1] - P_BUTT_F * ph))
    bg.alpha_composite(poet, (ax, ay))
    print('   сиденье (%.0f, %.0f), поэт %d px в (%d,%d): таз %+.0f, ступни y=%.0f'
          % (seat[0], seat[1], ph, ax, ay, ay + P_BUTT_F * ph - seat[1], ay + P_FEET_F * ph))

    box = (0, int(H * 0.34), int(W * 0.60), H)
    crop = bg.convert('RGB').crop(box).resize((int(W * 0.60 * 1.05), int(H * 0.66 * 1.05)),
                                             Image.LANCZOS)
    return bg, crop


def main():
    bgA, cropA = build(OLD, 'A старая')
    bgB, cropB = build(NEW, 'B новая')

    # лист 1: целиком оба кадра, рядом
    fullA = bgA.convert('RGB').resize((1280, 720), Image.LANCZOS)
    fullB = bgB.convert('RGB').resize((1280, 720), Image.LANCZOS)
    sh = Image.new('RGB', (2560, 720), (255, 255, 255))
    sh.paste(fullA, (0, 0))
    sh.paste(fullB, (1280, 0))
    d = ImageDraw.Draw(sh)
    for i, t in enumerate(('A — твоя скамейка', 'B — новая скамейка')):
        d.rectangle([i * 1280 + 12, 12, i * 1280 + 330, 56], fill=(255, 255, 255))
        d.text((i * 1280 + 22, 24), t, fill=(180, 0, 0))
    p1 = os.path.join(OUT, 'compare_full.jpg')
    sh.save(p1, quality=88)
    print('saved', os.path.relpath(p1, HERE), sh.size, os.path.getsize(p1), 'B')

    # лист 2: крупно, только скамейка с поэтом
    cw, ch = cropA.size
    sh2 = Image.new('RGB', (cw * 2, ch), (255, 255, 255))
    sh2.paste(cropA, (0, 0))
    sh2.paste(cropB, (cw, 0))
    d2 = ImageDraw.Draw(sh2)
    for i, t in enumerate(('A', 'B')):
        d2.rectangle([i * cw + 12, 12, i * cw + 70, 58], fill=(255, 255, 255))
        d2.text((i * cw + 30, 24), t, fill=(180, 0, 0))
    p2 = os.path.join(OUT, 'compare_bench.jpg')
    sh2.save(p2, quality=90)
    print('saved', os.path.relpath(p2, HERE), sh2.size, os.path.getsize(p2), 'B')


if __name__ == '__main__':
    main()
