# -*- coding: utf-8 -*-
"""Разбор правой (дальней) части новой скамейки: где именно низ ножек.

Иван: «правая сторона взлетела, должна быть на 30–40 см ниже; правая задняя ножка
летает». Значит надо точно знать, где кончаются ножки, а где доски. Печатаю карту
маски и профиль низа с выделением «ножек» (узкие столбцы, уходящие ниже досок).
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '_sat', 'prop_bench_new_matte.png')
im = Image.open(P).convert('RGBA')
a = np.asarray(im)
m = a[:, :, 3] > 140
Hf, Wf = m.shape
print('файл %dx%d' % (Wf, Hf))

cols, rows = 96, 40
bx, by = Wf / cols, Hf / rows
print('     ' + ''.join(str((i // 10) % 10) for i in range(cols)))
for j in range(rows):
    y0, y1 = int(j * by), max(int(j * by) + 1, int((j + 1) * by))
    row = ''
    for i in range(cols):
        x0, x1 = int(i * bx), max(int(i * bx) + 1, int((i + 1) * bx))
        v = m[y0:y1, x0:x1].mean()
        row += '#' if v > 0.75 else ('+' if v > 0.4 else ('.' if v > 0.12 else ' '))
    print('%4d %s' % (int(j * by), row))

print('\nпрофиль низа (каждые 1.5% ширины): x, низ маски')
bot = []
for x in range(Wf):
    c = np.nonzero(m[:, x])[0]
    bot.append(c.max() if c.size else -1)
bot = np.array(bot)
for frac in np.arange(0.02, 1.0, 0.015):
    x = int(frac * Wf)
    print('  x=%.3f (%4d)  низ %4d' % (frac, x, bot[x]))
