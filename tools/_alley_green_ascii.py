# -*- coding: utf-8 -*-
"""ASCII-карта «зелёности»: где газон/хвоя, а где серый асфальт.

green = G - (R+B)/2 (в 0..255). Асфальт и небо — около нуля/слабо отрицательные,
трава и хвоя — заметно положительные. Печатает 96x40 и границы газона по строкам.
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
green = a[:, :, 1] - (a[:, :, 0] + a[:, :, 2]) / 2.0

cols, rows = 96, 40
bx, by = W / cols, H / rows
chars = ' .:-=+*#%@'   # чем зеленее, тем плотнее символ
lo, hi = -6.0, 18.0
print('зелёность (G - (R+B)/2), порог 0 -> символ "=", 96 колонок')
print('    ' + ''.join(str((i // 10) % 10) for i in range(cols)))
for j in range(rows):
    y0, y1 = int(j * by), int((j + 1) * by)
    row = ''
    for i in range(cols):
        x0, x1 = int(i * bx), int((i + 1) * bx)
        v = green[y0:y1, x0:x1].mean()
        k = int((v - lo) / (hi - lo) * (len(chars) - 1))
        row += chars[max(0, min(len(chars) - 1, k))]
    print('%3d %s' % (int(y0 * 1080 / 540), row))

print('\nправый край газона слева (первая колонка, где green < 1), x в пикселях 1920:')
for y in range(int(H * 0.55), H, 10):
    row = green[y]
    k = np.ones(11) / 11.0
    rs = np.convolve(row, k, mode='same')
    idx = np.nonzero(rs < 1.0)[0]
    if idx.size:
        print('  y=%4d  x=%4.0f' % (y * 1080 / 540, idx.min() * 1920 / 960))
