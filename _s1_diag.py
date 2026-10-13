# -*- coding: utf-8 -*-
"""Диагностика S1: карта яркости (где стена/арка/человек) + проверка, куда лёг варп."""
import os
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A = np.asarray(Image.open(os.path.join(HERE, 'vn2', 'img', 'prolog', 's1.png')).convert('L'), np.float32)
H, W = A.shape
print('s1', W, 'x', H)
cols, rows = 12, 8
print('карта яркости (0-255), col→ :')
for r in range(rows):
    line = []
    for c in range(cols):
        blk = A[r * H // rows:(r + 1) * H // rows, c * W // cols:(c + 1) * W // cols]
        line.append('%3d' % int(blk.mean()))
    print('r%d ' % r + ' '.join(line))
print()
print('столбцы x-границ:', [c * W // cols for c in range(cols)])
print('строки y-границ:', [r * H // rows for r in range(rows)])

C = np.asarray(Image.open(os.path.join(HERE, 'assets', 'review', 'review_84_s1_katobus_v2.png')).convert('L'), np.float32)
# C — склейка 3 кадров по вертикали, вырежем вариант C (третий)
h1 = round(H * 1920 / 1920)  # 1080
print('склейка', C.shape)
