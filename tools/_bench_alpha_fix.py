# -*- coding: utf-8 -*-
"""Правая часть скамейки бледная: усилить альфу, чтобы не растворялась.

Замер (`_bench_faint.py`): у правого конца пропа альфа 38…160 вместо 255, но цвет уже
настоящий (R130 G121 B116 — дерево). Причём на x≈1220–1240 исходника идёт постоянная
полупрозрачная вертикаль от y 250 до 450 — это и есть правая передняя ножка, просто
нарисованная очень бледно. Дорисовывать не нужно, нужно поднять альфу.

Делает три силы усиления (GAINS) и собирает лист для показа.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
SPR = os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')
OUT = os.path.join(ROOT, '_sat')

VARIANTS = [
    ('v1', 0.60, 0.80),   # гамма, начало усиления (доля ширины файла)
    ('v2', 0.45, 0.74),
    ('v3', 0.33, 0.68),
]


def boost(path_in, gamma, x_start):
    im = Image.open(path_in).convert('RGBA')
    a = np.asarray(im).astype(np.float32)
    alpha, rgb = a[:, :, 3], a[:, :, :3]
    Hf, Wf = alpha.shape
    xs = np.arange(Wf, dtype=np.float32) / Wf
    # вес: 0 до x_start, 1 после x_start+0.10 — плавно
    w = np.clip((xs - x_start) / 0.10, 0.0, 1.0)
    w = w * w * (3 - 2 * w)
    gain = (255.0 * np.power(alpha / 255.0, gamma)) - alpha
    new_alpha = alpha + gain * w[None, :]
    # цвет бледных пикселей подтянуть к «дереву»: чуть темнее и плотнее
    lum = rgb.mean(axis=2, keepdims=True)
    pull = (1.0 - lum / 255.0).clip(0, 1) * 0.0  # без изменения цвета (проверено)
    new_rgb = np.clip(rgb * (1 - pull) + (rgb * 0.92) * pull, 0, 255)
    out = np.dstack([new_rgb, np.clip(new_alpha, 0, 255)]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA'), float(w.sum() / max(1, (w > 0.01).sum()))


def main():
    W, H = 1920, 1080
    Y_H, K = 572.0, 1.146
    Y_LEG, X_LEG = 960.0, 148.0
    LEG_X_F, LEG_Y_F, BACK_TOP_F = 0.10, 0.881, 0.160
    SEAT_F, GROUND_F, BUTT_FX = 0.624, 0.986, 0.295
    P_HEAD_F, P_FEET_F, P_BUTT_F = 201 / 1433.0, 1419 / 1433.0, 0.625
    VANISH = (1037.0, 572.0)

    BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
    POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
    KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')

    alley_deg = np.degrees(np.arctan2(Y_LEG - VANISH[1], VANISH[0] - X_LEG))
    ROT = alley_deg - 26.2
    m = K * (Y_LEG - Y_H)
    h_file = 0.90 * m / (LEG_Y_F - BACK_TOP_F)

    bg0 = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    def put(canvas, path, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
        im = Image.open(path).convert('RGBA')
        h = round(H * height_pct / 100.0)
        w = round(im.width * h / im.height)
        im = im.resize((w, h), Image.LANCZOS)
        canvas.alpha_composite(im, (round(W * left_pct / 100.0 - w / 2.0),
                                    round(H * (1.0 - bottom_pct / 100.0)) - h))

    put(bg0, KATE, 73, 99, -3)

    results = []
    for name, gamma, x_start in VARIANTS:
        prop_img, wmean = boost(SPR, gamma, x_start)
        prop0 = prop_img.resize((max(1, round(prop_img.width * h_file / prop_img.height)),
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
        sp = moved(BUTT_FX * prop0.width, SEAT_F * prop0.height)
        seat = (paste[0] + sp[0], paste[1] + sp[1])

        canvas = bg0.copy()
        canvas.alpha_composite(prop, paste)
        poet = Image.open(POET).convert('RGBA')
        ph = 780
        pw = round(poet.width * ph / poet.height)
        poet = poet.resize((pw, ph), Image.LANCZOS)
        canvas.alpha_composite(poet, (int(round(seat[0] - pw / 2.0)),
                                      int(round(seat[1] - P_BUTT_F * ph))))
        p = os.path.join(OUT, 'alley_bench_%s.jpg' % name)
        canvas.convert('RGB').save(p.replace('.jpg', '_full.jpg'), quality=90)
        canvas.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p, quality=88)
        print('%s: гамма %.2f от x=%.2f -> %s %d B' % (name, gamma, x_start,
                                                        os.path.relpath(p, HERE),
                                                        os.path.getsize(p)))
        results.append((name, canvas))

    # лист: кроп вокруг скамейки, три варианта
    box = (0, int(H * 0.34), int(W * 0.62), H)
    crops = [c.convert('RGB').crop(box) for _, c in results]
    cw, ch = crops[0].size
    sheet = Image.new('RGB', (cw * 3, ch), (250, 250, 250))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(crops):
        sheet.paste(c, (cw * i, 0))
        d.rectangle([cw * i + 10, 10, cw * i + 80, 60], fill=(255, 255, 255))
        d.text((cw * i + 30, 24), 'ABC'[i], fill=(200, 0, 0))
    ps = os.path.join(OUT, 'bench_alpha_sheet.jpg')
    sheet.save(ps, quality=86)
    print('saved', os.path.relpath(ps, HERE), sheet.size, os.path.getsize(ps), 'B')


if __name__ == '__main__':
    main()
