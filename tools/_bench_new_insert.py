# -*- coding: utf-8 -*-
"""Вырезать новую скамейку по белому фону и вставить в сцену аллеи.

Шаги:
 1) матирование: белое (яркость>243 и насыщенность<0.06) -> прозрачно, с мягким краем;
 2) замер: ось пропа (PCA по маске), верх и низ ближнего торца в левой трети;
 3) масштаб: высота ближнего торца (верх спинки -> низ ножки) = 0.90 м, из m(y) сцены;
 4) посадка поэта: таз на 0.5 высоты торца, доля 0.295 по длине.
Сохраняет `_sat/bench_new_matte.png` и превью `_sat/alley_prev10.jpg`.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H = 1920, 1080
Y_H, K = 572.0, 1.146
VANISH = (1037.0, 572.0)

SRC = os.path.join(ROOT, 'assets', 'gen', 'prop_bench_new_0.png')
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
OUT = os.path.join(ROOT, '_sat')

Y_LEG = float(os.environ.get('Y_LEG', 960))
X_LEG = float(os.environ.get('X_LEG', 148))
BACK_H = 0.90
P_HEAD_F, P_FEET_F, P_BUTT_F = 201 / 1433.0, 1419 / 1433.0, 0.625


def matte(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32)
    lum = a.mean(axis=2)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1.0)
    white = (lum > 243) & (sat < 0.06)
    alpha = np.where(white, 0.0, 255.0)
    # мягкий край: где яркость 225..243 — полупрозрачно
    soft = (~white) & (lum > 225) & (sat < 0.10)
    alpha[soft] = np.clip((243.0 - lum[soft]) / 18.0 * 255.0, 0, 255)
    # убрать одиночные пиксели: минимум непрозрачных соседей
    m = alpha > 40
    pad = np.pad(m, 1)
    neigh = sum(pad[1 + dy:1 + dy + m.shape[0], 1 + dx:1 + dx + m.shape[1]]
                for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - m
    alpha[(m) & (neigh < 2)] = 0
    out = np.dstack([a, alpha]).astype(np.uint8)
    img = Image.fromarray(out, 'RGBA')
    bb = img.getchannel('A').point(lambda v: 255 if v > 60 else 0).getbbox()
    img = img.crop(bb)
    print('матирование: маска %d%% файла, bbox %s -> %dx%d'
          % (int(100.0 * (np.asarray(img)[:, :, 3] > 60).mean()), bb, img.width, img.height))
    return img


def main():
    img = matte(SRC)
    a = np.asarray(img)
    m = a[:, :, 3] > 140
    ys, xs = np.nonzero(m)
    Wf, Hf = img.size
    print('маска %dx%d: x %d..%d, y %d..%d' % (Wf, Hf, xs.min(), xs.max(), ys.min(), ys.max()))

    # ось
    X = np.stack([xs - xs.mean(), ys - ys.mean()], axis=1).astype(np.float64)
    C = X.T @ X / len(X)
    w, v = np.linalg.eigh(C)
    main_axis = v[:, np.argmax(w)]
    ang = np.degrees(np.arctan2(-main_axis[1], main_axis[0]))
    print('ось пропа (PCA): %.1f°' % ang)

    # ближний торец: левая треть
    left = m[:, :int(Wf * 0.35)]
    lys = np.nonzero(left.any(axis=1))[0]
    top_f, bot_f = lys.min(), lys.max()
    print('ближний торец: верх y=%d, низ y=%d, высота %d px' % (top_f, bot_f, bot_f - top_f))

    alley_deg = np.degrees(np.arctan2(Y_LEG - VANISH[1], VANISH[0] - X_LEG))
    ROT = alley_deg - ang
    m_scene = K * (Y_LEG - Y_H)
    need_back = BACK_H * m_scene
    k = need_back / (bot_f - top_f)
    print('сцена: %.0f px/м, ближний торец должен быть %.0f px -> коэффициент %.3f, поворот %.1f°'
          % (m_scene, need_back, k, ROT))

    scaled = img.resize((max(1, round(img.width * k)), max(1, round(img.height * k))),
                        Image.LANCZOS)
    top_s, bot_s = top_f * k, bot_f * k
    # x ближней ножки: самая левая колонка маски в нижней четверти торца
    leftcols = np.nonzero(m[:, :int(Wf * 0.3)].any(axis=0))[0]
    x_anchor_f = float(leftcols.min())
    ax, ay = x_anchor_f * k, bot_s
    rot = scaled.rotate(ROT, resample=Image.BICUBIC, expand=True, center=(ax, ay))
    th = np.deg2rad(ROT)
    cx, cy = scaled.width / 2.0, scaled.height / 2.0
    x, y = ax - cx, ay - cy
    nx = x * np.cos(th) + y * np.sin(th) + rot.width / 2.0
    ny = -x * np.sin(th) + y * np.cos(th) + rot.height / 2.0
    paste = (int(round(X_LEG - nx)), int(round(Y_LEG - ny)))
    print('вставка в (%d,%d), размер после поворота %dx%d' % (paste[0], paste[1], rot.width, rot.height))

    # сиденье = середина высоты ближнего торца
    seat_near = (Y_LEG + (bot_s - top_s) / 2.0 * -1 + 0.0)
    seat_near_y = Y_LEG - (bot_s - top_s) * 0.5
    along = 0.295 * 1.8 * m_scene
    seat_x = X_LEG + along * np.cos(np.deg2rad(ang))
    seat_y = seat_near_y - along * np.sin(np.deg2rad(ang))
    print('сиденье у торца y=%.0f, у поэта (%.0f, %.0f)' % (seat_near_y, seat_x, seat_y))

    bg = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')

    def put(canvas, path, left_pct=73.0, height_pct=99.0, bottom_pct=-3.0):
        im = Image.open(path).convert('RGBA')
        h = round(H * height_pct / 100.0)
        w = round(im.width * h / im.height)
        im = im.resize((w, h), Image.LANCZOS)
        canvas.alpha_composite(im, (round(W * left_pct / 100.0 - w / 2.0),
                                    round(H * (1.0 - bottom_pct / 100.0)) - h))

    put(bg, KATE, 73, 99, -3)
    bg.alpha_composite(rot, paste)

    poet = Image.open(POET).convert('RGBA')
    ph = int(os.environ.get('POET_H', 780))
    pw = round(poet.width * ph / poet.height)
    poet = poet.resize((pw, ph), Image.LANCZOS)
    bg.alpha_composite(poet, (int(round(seat_x - pw / 2.0)), int(round(seat_y - P_BUTT_F * ph))))
    print('поэт %d px в (%d,%d), таз y=%.0f, ступни y=%.0f'
          % (ph, int(seat_x - pw / 2.0), int(seat_y - P_BUTT_F * ph),
             seat_y, seat_y - P_BUTT_F * ph + P_FEET_F * ph))

    p = os.path.join(OUT, 'alley_prev10.jpg')
    bg.convert('RGB').resize((1280, 720), Image.LANCZOS).save(p, quality=88)
    bg.convert('RGB').save(os.path.join(OUT, 'alley_prev10_full.jpg'), quality=90)
    rot.save(os.path.join(OUT, 'bench_new_matte.png'))
    print('saved', os.path.relpath(p, HERE), os.path.getsize(p), 'B')


if __name__ == '__main__':
    main()
