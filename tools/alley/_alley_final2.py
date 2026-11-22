# -*- coding: utf-8 -*-
"""Финальная посадка поэта: +50 % к высоте, таз ложится на доску с заглублением.

Почему прошлый вариант «висел»: я выравнивал по F_SEAT = 0.6148 — это самая
нижняя точка силуэта в средней полосе, то есть ПРОМЕЖНОСТЬ между ног. Сидят же
задней частью, а её низ выше. Здесь контакт задаётся по низу ЗАДНЕЙ части тела,
а линия доски берётся из альфы пропа ровно в колонках, где сидит поэт.

SINK — насколько задница «утапливается» в доску (px кадра), чтобы не было
щели и не выглядело, будто она висит.
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
W, H_IMG = 1920, 1080
Y_H, K = 572.0, 1.146
OUT = os.path.join(ROOT, '_sat')

BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
POET = os.path.join(ROOT, 'vn2', 'img', 'char', os.environ.get('POET', 'poet_seat_upset.webp'))
KATE = os.path.join(ROOT, 'vn2', 'img', 'char', 'kate.webp')
PROP = os.path.join(OUT, 'wc', os.environ.get('PROP', 'prop_B.png'))

H_MULT = float(os.environ.get('H_MULT', '1.50'))
H_BASE = 517.73
F_TOP, F_FEET = 0.140, 0.9895
SINK = float(os.environ.get('SINK', '6'))
PREFIX = os.environ.get('PREFIX', 'FINAL')
GUIDES = os.environ.get('GUIDES', '0') == '1'

with open(os.path.join(OUT, 'poet_params.json')) as f:
    P = json.load(f)
PX, PY = P['px'], P['py']
POET_X = P['x_poet']


def bench_seat_line(prop_mask, cols_local):
    """верх доски сиденья (последняя длинная полоса) в заданных колонках пропа."""
    vals = []
    for x in cols_local:
        col = prop_mask[:, x]
        runs, s = [], None
        for y in range(len(col) + 1):
            v = col[y] if y < len(col) else False
            if v and s is None:
                s = y
            elif not v and s is not None:
                runs.append((s, y - 1))
                s = None
        if runs:
            vals.append(runs[-1][0])
    return float(np.median(vals)) if vals else None


def main():
    prop = Image.open(PROP).convert('RGBA')
    prop_mask = np.asarray(prop)[:, :, 3] > 60

    poet0 = Image.open(POET).convert('RGBA')
    h_px = int(round(H_BASE * H_MULT))
    w_px = max(1, round(poet0.width * h_px / poet0.height))
    poet = poet0.resize((w_px, h_px), Image.LANCZOS)
    pmask = np.asarray(poet)[:, :, 3] > 60

    # задняя часть тела в спрайте: колонки 36..60 % (там «полка» под бедром)
    b0, b1 = int(w_px * 0.36), int(w_px * 0.60)
    bottoms = []
    for x in range(b0, b1):
        idx = np.nonzero(pmask[:, x])[0]
        if idx.size:
            bottoms.append(idx.max())
    butt_bottom = int(np.percentile(bottoms, 90))   # самый низкий край этой зоны
    print('спрайт %dx%d, низ задней зоны (строка %d из %d)' % (w_px, h_px, butt_bottom, h_px))

    # колонки пропа, над которыми сидит поэт
    pl_try = POET_X - w_px // 2
    cols_local = [x - PX for x in range(pl_try + b0, pl_try + b1)
                  if 0 <= x - PX < prop.width]
    seat_local = bench_seat_line(prop_mask, cols_local)
    seat_frame = PY + seat_local
    print('линия доски под поэтом: проп y=%.0f -> кадр %.1f (в %d колонках)'
          % (seat_local, seat_frame, len(cols_local)))

    # низ задницы = линия доски + SINK
    target_butt = seat_frame + SINK
    pt = int(round(target_butt - butt_bottom))
    feet_y = pt + F_FEET * h_px
    top_y = pt + F_TOP * h_px
    m_feet = K * (feet_y - Y_H)
    fig_m = (F_FEET - F_TOP) * h_px / m_feet
    print('верх спрайта %d, задница %.0f (доска %.1f, утопление %+.1f px)'
          % (pt, pt + butt_bottom, seat_frame, pt + butt_bottom - seat_frame))
    print('ступни %.0f, фигура %.0f px = %.2f м при %.0f px/м' % (feet_y, (F_FEET - F_TOP) * h_px,
                                                                  fig_m, m_feet))

    canvas = Image.open(BG).convert('RGB').resize((W, H_IMG), Image.LANCZOS).convert('RGBA')

    kate = Image.open(KATE).convert('RGBA')
    kh = round(H_IMG * 0.99)
    kw = round(kate.width * kh / kate.height)
    kate = kate.resize((kw, kh), Image.LANCZOS)
    canvas.alpha_composite(kate, (round(W * 0.73 - kw / 2.0), round(H_IMG * 1.03) - kh))

    rows = np.nonzero(prop_mask.any(axis=1))[0]
    flat = prop.split()[3].resize((prop.width, max(1, int(prop.height * 0.16))),
                                  Image.LANCZOS).filter(ImageFilter.GaussianBlur(9))
    shadow = Image.new('RGBA', flat.size, (34, 42, 36, 0))
    shadow.putalpha(flat.point(lambda v: int(v * 0.42)))
    canvas.alpha_composite(shadow, (PX, PY + rows.max() - flat.size[1] // 2))
    canvas.alpha_composite(prop, (PX, PY))

    canvas.alpha_composite(poet, (pl_try, pt))

    # контроль по пикселям финального кадра
    full_mask = np.zeros((H_IMG, W), bool)
    full_mask[pt:pt + h_px, pl_try:pl_try + w_px] = pmask
    bench_full = np.zeros((H_IMG, W), bool)
    bench_full[PY:PY + prop.height, PX:PX + prop.width] = prop_mask
    inter = (full_mask & bench_full).sum()

    # щель: для каждой колонки задней зоны — есть ли между низом тела и доской просвет
    gaps = []
    for xf in range(pl_try + b0, min(pl_try + b1, W)):
        col = full_mask[:, xf]
        idx = np.nonzero(col)[0]
        if not idx.size:
            continue
        body_bottom = idx.max()
        bcol = bench_full[:, xf]
        bidx = np.nonzero(bcol)[0]
        if not bidx.size:
            continue
        # верх доски в этой колонке = первая строка последней длинной полосы
        runs, s = [], None
        n = len(bcol)
        for y in range(n + 1):
            v = bcol[y] if y < n else False
            if v and s is None:
                s = y
            elif not v and s is not None:
                if y - s > 8:
                    runs.append((s, y - 1))
                s = None
        if not runs:
            continue
        board_top = runs[-1][0]
        gaps.append(body_bottom - board_top)
    if gaps:
        gaps = np.array(gaps)
        print('щель тело↔доска по %d колонкам: медиана %+.0f px, макс %+.0f (плюс = тело ниже доски)'
              % (len(gaps), np.median(gaps), gaps.max()))
    print('пересечение силуэтов: %d px' % inter)

    if GUIDES:
        d = ImageDraw.Draw(canvas)
        d.line([(0, seat_frame), (W, seat_frame)], fill=(255, 0, 200), width=3)
        d.line([(0, feet_y), (W, feet_y)], fill=(255, 160, 0), width=3)
        d.line([(0, 960), (W, 960)], fill=(0, 200, 255), width=3)

    out = canvas.convert('RGB')
    out.save(os.path.join(OUT, PREFIX + '_full.jpg'), quality=90)
    out.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, PREFIX + '.jpg'), quality=88)
    z = out.crop((110, 180, 830, 1080))
    z.save(os.path.join(OUT, PREFIX + '_zoom.jpg'), quality=94)
    bz = out.crop((230, 600, 620, 900))
    bz = bz.resize((int(bz.width * 2.2), int(bz.height * 2.2)), Image.LANCZOS)
    bz.save(os.path.join(OUT, PREFIX + '_butt.jpg'), quality=95)
    print('saved %s_{full,zoom,butt}.jpg' % PREFIX)

    with open(os.path.join(OUT, 'final_params.json'), 'w') as f:
        json.dump(dict(h_mult=H_MULT, h_px=h_px, top=pt, left=pl_try, feet=feet_y,
                       seat=int(seat_frame), butt=int(pt + butt_bottom), sink=SINK,
                       fig_m=round(fig_m, 3)), f, indent=2)


if __name__ == '__main__':
    main()
