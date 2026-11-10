# -*- coding: utf-8 -*-
"""Посадка новой скамейки под поэта: CSS-числа считаются, а не подбираются на глаз.

Дано (замеры, не допущения):
  • масштаб кадра: Екатерина 1.70 м = 738 px при сцене 757 px -> 434 px/м;
  • сидящий поэт: фигура = 0.85 холста (`_seat_fill_norm.py`), низ холста на 3 % НИЖЕ
    края сцены (`.sprite{bottom:-3%}`), ступни на 1 % холста выше низа,
    бёдра = 0.346 высоты фигуры от ступней;
  • скамейка: у ближнего торца спинка 0.90 м, сиденье на 0.45 м (половина высоты),
    земля у ближнего торца ставится на линию ступней поэта.

Печатает готовые `h`, `bottom`, `left` для узла alley и высоту сидящего спрайта.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROP = os.path.join(HERE, 'assets', 'sprites', 'prop_bench.png')

STAGE_W, STAGE_H = 1346.0, 757.0
PX_PER_M = 738.0 / 1.70
SPRITE_BOTTOM = 0.03          # .sprite{bottom:-3%}: низ холста ниже края сцены
FILL = 0.85
BOTTOM_PAD = 0.01
HIP = 0.346
SEATED_H_M = 1.30
BENCH_TOP_M = 0.90
BENCH_SEAT_M = 0.45
SLOT0 = 0.27
BENCH_FRAC_ALONG = 0.25

# ---------- поэт ----------
fig_px = SEATED_H_M * PX_PER_M
canvas_px = fig_px / FILL
poet_h_pct = 100.0 * canvas_px / STAGE_H
sprite_bottom_y = STAGE_H * (1 + SPRITE_BOTTOM)
feet_y = sprite_bottom_y - BOTTOM_PAD * canvas_px
hip_y = feet_y - HIP * fig_px
print('масштаб кадра %.1f px/м' % PX_PER_M)
print('поэт: фигура %.0f px = %.2f м, холст %.0f px -> height: %.1f%% сцены'
      % (fig_px, fig_px / PX_PER_M, canvas_px, poet_h_pct))
print('  ступни y=%.0f, бёдра (линия сиденья) y=%.0f' % (feet_y, hip_y))

# ---------- скамейка ----------
im = Image.open(PROP).convert('RGBA')
m = np.asarray(im.split()[-1]) > 140
ys, xs = np.nonzero(m)
x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
print('\nпроп %dx%d, плотная маска x %d..%d y %d..%d'
      % (im.width, im.height, x0, x1, y0, y1))


def band_stats(lo, hi):
    a, b = int(x0 + lo * (x1 - x0)), int(x0 + hi * (x1 - x0))
    tops, bots = [], []
    for x in range(a, b + 1):
        col = np.nonzero(m[:, x])[0]
        if len(col):
            tops.append(col.min())
            bots.append(col.max())
    if not tops:
        return None
    return float(np.median(tops)), float(np.median(bots))


left_band, right_band = band_stats(0.05, 0.20), band_stats(0.80, 0.95)
near_is_left = (left_band[1] - left_band[0]) >= (right_band[1] - right_band[0])
top_px, ground_px = left_band if near_is_left else right_band
far_top, far_ground = right_band if near_is_left else left_band
near_h = ground_px - top_px
print('ближний торец: %s, верх спинки y=%.0f, земля y=%.0f, высота %.0f px'
      % ('левый' if near_is_left else 'правый', top_px, ground_px, near_h))
print('дальний торец: верх %.0f, земля %.0f, высота %.0f px (%.2f от ближнего)'
      % (far_top, far_ground, far_ground - far_top, (far_ground - far_top) / near_h))
print('сиденье по маске на 0.50 высоты ближнего торца (ожидаем 0.50)')

s = BENCH_TOP_M * PX_PER_M / near_h
prop_h = im.height * s
prop_w = im.width * s
print('\nмасштаб пропа: %.4f -> на экране %.0f x %.0f px' % (s, prop_w, prop_h))

seat_px = BENCH_SEAT_M * PX_PER_M
# низ КАРТИНКИ пропа ниже земли у ближнего торца (под ножкой штрих/тень до y=%d)
prop_bottom_y = feet_y + (float(y1) - ground_px) * s
seat_y = feet_y - seat_px
print('проп: земля у ближнего торца y=%.0f (ступни поэта y=%.0f), низ картинки y=%.0f'
      % (feet_y, feet_y, prop_bottom_y))
print('сиденье y=%.0f, бёдра поэта y=%.0f -> разница %+.0f px (%+.1f см)'
      % (seat_y, hip_y, seat_y - hip_y, (seat_y - hip_y) / PX_PER_M * 100))

h_pct = 100.0 * prop_h / STAGE_H
bottom_pct = -100.0 * (prop_bottom_y - STAGE_H) / STAGE_H
x_along_px = (x0 + BENCH_FRAC_ALONG * (x1 - x0)) * s
if not near_is_left:
    x_along_px = (x1 - BENCH_FRAC_ALONG * (x1 - x0)) * s
prop_left_x = SLOT0 * STAGE_W - x_along_px
left_pct = 100.0 * (prop_left_x + prop_w / 2.0) / STAGE_W

print('\n--- для узла alley ---')
print("'prop': {'src': 'img/prop/bench.webp', 'left': '%.0f%%', 'bottom': '%.1f%%', "
      "'h': '%.0f%%'}" % (left_pct, bottom_pct, h_pct))
print('края пропа по x: %.0f..%.0f (сцена 0..%.0f), поэт x=%.0f, Екатерина x=%.0f'
      % (prop_left_x, prop_left_x + prop_w, STAGE_W, SLOT0 * STAGE_W, 0.73 * STAGE_W))
print('верх спинки на экране y=%.0f, макушка поэта y=%.0f (разница %.0f px = %.2f м)'
      % (prop_bottom_y - prop_h + top_px * s, feet_y - fig_px,
         (feet_y - fig_px) - (prop_bottom_y - prop_h + top_px * s),
         ((feet_y - fig_px) - (prop_bottom_y - prop_h + top_px * s)) / PX_PER_M))
print('\n--- для style.css ---')
print('.sprite.seated{height:%.0f%%}' % poet_h_pct)
