# -*- coding: utf-8 -*-
"""ASCII-карта «дорожной» маски: где в кадре светлый ровный асфальт.

Символы: '#' — асфальт (светло, мало насыщенности), '+' — полутон, '.' — газон/хвоя,
' ' — тёмное. Печатается 96 колонок х 40 строк, с номерами строк кадра.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')
W, H = 960, 540

im = Image.open(BG).convert('RGB').resize((W, H), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
lum = a.mean(axis=2)
mx = a.max(axis=2)
mn = a.min(axis=2)
sat = (mx - mn) / np.maximum(mx, 1.0)
road = (lum / 255.0) * (1.0 - sat)

cols, rows = 96, 40
bx, by = W / cols, H / rows
chars = ' .:+*#%@'
print('дорожная метрика, 96 колонок (лево..право), 40 строк (верх..низ)')
print('    ' + ''.join(str((i // 10) % 10) for i in range(cols)))
for j in range(rows):
    y0, y1 = int(j * by), int((j + 1) * by)
    ys = []
    for i in range(cols):
        x0, x1 = int(i * bx), int((i + 1) * bx)
        v = road[y0:y1, x0:x1].mean()
        ys.append(chars[min(len(chars) - 1, int(v * len(chars)))])
    print('%3d %s' % (int(y0 * 1080 / 540), ''.join(ys)))

# профиль: для каждой строки — левая и правая граница «сильного асфальта» (>= 0.55)
print('\nграницы асфальта по строкам (метрика >= 0.55), x в пикселях 1920:')
for y in range(int(H * 0.52), H, 8):
    row = road[y]
    idx = np.nonzero(row >= 0.55)[0]
    if idx.size < 10:
        continue
    print('  y=%4d  левая x=%4.0f  правая x=%4.0f  ширина %4.0f'
          % (y * 1080 / 540, idx.min() * 1920 / 960, idx.max() * 1920 / 960,
             (idx.max() - idx.min()) * 1920 / 960))
