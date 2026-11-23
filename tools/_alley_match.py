# -*- coding: utf-8 -*-
"""Сверка ЖИВОГО кадра сцены «аллея» с принятым офлайн-кадром C
(`_sat/final_B_full.jpg`, `tools/alley/_alley_final2.py`, H_MULT=1.50).

Если проводка (фон + проп + посадка спрайта) верна, кадры совпадают с точностью
до сжатия JPEG/WebP. Считаю MAE по всему кадру и по области скамейки.

Запуск: python3 tools/_alley_match.py
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAT = os.path.join(ROOT, '_sat')

live = Image.open(os.path.join(SAT, 'alley_clean_desk.png')).convert('RGB')
ref = Image.open(os.path.join(SAT, 'final_B_full.jpg')).convert('RGB').resize(live.size, Image.LANCZOS)
a = np.asarray(live, np.int16)
b = np.asarray(ref, np.int16)
d = np.abs(a - b).mean(axis=2)
print('кадр %s' % (live.size,))
print('MAE по всему кадру: %.2f (из 255)' % d.mean())

# область скамейки на живом кадре: проп 26.875% / 9.352% / 48.704% на 1280x720
W, H = live.size
px = 0.26875 * W
py_bottom = 0.09352 * H
ph = 0.48704 * H
pw = ph * 876 / 526
x0, x1 = int(px - pw / 2), int(px + pw / 2)
y0, y1 = int(H - py_bottom - ph), int(H - py_bottom)
sub = d[max(0, y0):y1, max(0, x0):x1]
print('область скамейки %dx%d: MAE %.2f, пикселей >40: %.1f%%'
      % (sub.shape[1], sub.shape[0], sub.mean(), 100.0 * (sub > 40).mean()))

# карта разницы — глазами Ивана (яркое = расхождение)
vis = np.zeros(d.shape + (3,), np.uint8)
vis[..., 0] = np.clip(d * 4, 0, 255)
Image.fromarray(vis).save(os.path.join(SAT, 'alley_match_diff.png'))
print('карта разницы: _sat/alley_match_diff.png')

# сдвиг: если проводка геометрии верна, лучший сдвиг — (0, 0)
x0, x1, y0, y1 = 90, 560, 150, 660
best = None
for dy in range(-10, 11):
    for dx in range(-10, 11):
        m = float(np.abs(a[y0:y1, x0:x1] - b[y0 + dy:y1 + dy, x0 + dx:x1 + dx]).mean())
        if best is None or m < best[0]:
            best = (m, dx, dy)
print('лучший сдвиг: dx=%d dy=%d (MAE %.2f; при 0,0 — %.2f)'
      % (best[1], best[2], best[0], float(np.abs(a[y0:y1, x0:x1] - b[y0:y1, x0:x1]).mean())))

