# -*- coding: utf-8 -*-
"""Посадка поэта НА доску по замеру, а не на глаз.

Замеры, на которых всё держится:
  * верх доски сиденья берётся из альфы пропа: над сиденьем идут три доски спинки,
    между ними прозрачные зазоры, поэтому последняя сплошная полоса = сиденье;
  * земля под поэтом считается по m(y) = 1.146*(y-572) итерацией.

Дальше две жёсткие связи:
  * таз (доля F_BUTT файла) стоит ровно на верхней плоскости доски;
  * ступни (доля 0.988) стоят на земле.
Из них высота спрайта H = (земля − доска) / (0.988 − F_BUTT), то есть она не
выбирается «на глаз», а следует из геометрии кадра.

F_BUTT по анатомии: сидящий человек от ступней до макушки ~1.32–1.40 м,
фигура занимает 0.828 файла, сиденье 0.45 м -> F_BUTT = 0.988 − 0.3726/h_m.
"""
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
W, H_IMG = 1920, 1080
Y_H, K = 572.0, 1.146
Y_GROUND_LEG = 960.0
POET = os.path.join(ROOT, 'vn2', 'img', 'char', 'poet_seat_upset.webp')
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
F_FEET, F_TOP = 0.988, 0.16
PROP_W = 876


def m_of(y):
    return K * (y - Y_H)


def ground_at(y_seat):
    g = y_seat + 0.45 * m_of(y_seat)
    for _ in range(40):
        g = y_seat + 0.45 * m_of(g)
    return g


def seat_top_of(prop_path, x):
    a = np.asarray(Image.open(prop_path).convert('RGBA'))[:, :, 3]
    col = a[:, x] > 60
    runs, s = [], None
    for y in range(len(col) + 1):
        v = col[y] if y < len(col) else False
        if v and s is None:
            s = y
        elif not v and s is not None:
            runs.append((s, y - 1))
            s = None
    # сиденье — последняя полоса, которая заметно длиннее досок спинки
    boards = runs[:-1]
    return runs[-1][0] if runs else None, boards, runs


def place(prop_path, px, py, f_butt, h_m, label, out_dir):
    seat_local, _, runs = seat_top_of(prop_path, int(os.environ.get('SEAT_X', '343')))
    seat_frame = py + seat_local
    ground = ground_at(seat_frame)
    h_px = (ground - seat_frame) / (F_FEET - f_butt)
    print('%s: доска в пропе y=%d -> кадр %d, земля %.0f, H=%.0f px, F_BUTT=%.3f'
          % (label, seat_local, seat_frame, ground, h_px, f_butt))
    poet = Image.open(POET).convert('RGBA')
    w = max(1, round(poet.width * h_px / poet.height))
    poet = poet.resize((w, int(round(h_px))), Image.LANCZOS)
    # ставим по ступням на землю
    return poet, int(round(ground - F_FEET * h_px)), ground, seat_frame


def main():
    import sys
    sys.path.insert(0, HERE)
    PROP = os.path.join(ROOT, '_sat', 'wc', os.environ.get('PROP', 'prop_B.png'))
    PREFIX = os.environ.get('PREFIX', 'sit_B')
    BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
    OUT = os.path.join(ROOT, '_sat')

    prop = Image.open(PROP).convert('RGBA')
    a = np.asarray(prop)[:, :, 3]
    m = a > 60
    rows = np.nonzero(m.any(axis=1))[0]
    cols = np.nonzero(m.any(axis=0))[0]
    px = int(round(0.2856 * Y_GROUND_LEG - 108.5 + 15 - cols.min()))
    py = int(round(Y_GROUND_LEG - rows.max()))

    variants = []
    for h_m, f_butt in ((1.32, 0.988 - 0.3726 / 1.32), (1.40, 0.988 - 0.3726 / 1.40)):
        poet, top, ground, seat_frame = place(PROP, px, py, f_butt, h_m,
                                              'h=%.2fм' % h_m, OUT)
        canvas = Image.open(BG).convert('RGB').resize((W, H_IMG), Image.LANCZOS).convert('RGBA')
        kate = Image.open(KATE).convert('RGBA')
        kh = round(H_IMG * 0.99)
        kw = round(kate.width * kh / kate.height)
        kate = kate.resize((kw, kh), Image.LANCZOS)
        canvas.alpha_composite(kate, (round(W * 0.73 - kw / 2.0), round(H_IMG * 1.03) - kh))

        flat = prop.split()[3].resize((prop.width, max(1, int(prop.height * 0.16))),
                                      Image.LANCZOS).filter(ImageFilter.GaussianBlur(9))
        shadow = Image.new('RGBA', flat.size, (34, 42, 36, 0))
        shadow.putalpha(flat.point(lambda v: int(v * 0.42)))
        canvas.alpha_composite(shadow, (px, py + rows.max() - flat.size[1] // 2))
        canvas.alpha_composite(prop, (px, py))

        # x поэта: 0.40 м от ближнего торца вдоль сиденья
        x_poet = int(os.environ.get('POET_X', '421'))
        canvas.alpha_composite(poet, (x_poet - poet.width // 2, top))
        variants.append((('%s' % os.environ.get('LABEL', 'h')), canvas, h_m, f_butt))
        canvas.convert('RGB').save(os.path.join(OUT, PREFIX + '_h%d_full.jpg' % round(h_m * 100)),
                                   quality=90)

        # проверка: где низ силуэта поэта в кадре
        pa = np.asarray(poet)[:, :, 3] > 60
        bot = np.nonzero(pa.any(axis=1))[0].max()
        print('   проверка: силуэт поэта низ %d, земля %.0f (разница %+d px)'
              % (top + bot, ground, top + bot - int(round(ground))))

    sh = Image.new('RGB', ((variants[0][1].width // 2 + 10) * len(variants), 640), (250, 250, 248))
    for i, (lab, canvas, h_m, f_butt) in enumerate(variants):
        c = canvas.convert('RGB').crop((100, 420, 900, 1080)).resize((790, 650), Image.LANCZOS)
        c = c.crop((0, 0, 790, 640))
        sh.paste(c, (i * (790 + 10), 0))
    p = os.path.join(OUT, PREFIX + '_sit.png')
    sh.save(p)
    print('saved', os.path.relpath(p, HERE), sh.size, os.path.getsize(p), 'B')
    for i, (lab, canvas, h_m, f_butt) in enumerate(variants):
        canvas.convert('RGB').crop((100, 420, 900, 1080)).save(
            os.path.join(OUT, '%s_%d.jpg' % (PREFIX, i)), quality=93)


if __name__ == '__main__':
    main()
