# -*- coding: utf-8 -*-
"""Проверка: попал ли мел в кадр (в квадре стало светлее) и где вообще стена."""
import os
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
src = np.asarray(Image.open(os.path.join(HERE, 'vn2', 'img', 'prolog', 's1.png')).convert('L'), np.float32)
Q = {
    'C': [(168, 600), (470, 636), (470, 812), (168, 764)],
    'D': [(880, 255), (1230, 300), (1230, 600), (880, 505)],
    'E': [(950, 330), (1360, 362), (1360, 700), (950, 648)],
    'F': [(1500, 300), (1860, 344), (1860, 648), (1500, 586)],
}
sheet = Image.open(os.path.join(HERE, 'assets', 'review', 'review_84_s1_katobus_v2.png')).convert('L')
A = np.asarray(sheet, np.float32)
rh, caph, hdr, gap, pad = 1080, 44, 82, 10, 20
print('лист', A.shape)
labels = ['A', 'B', 'C', 'D', 'E', 'F']
for i, lb in enumerate(labels):
    y0 = hdr + i * (rh + caph + gap)
    crop = A[y0:y0 + rh, pad:pad + 1920]
    print(lb, 'средняя яркость кадра = %.1f' % crop.mean())
for lb, q in Q.items():
    xs = [p[0] for p in q]; ys = [p[1] for p in q]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    print(lb, 'квадр', (x0, y0, x1, y1), 'яркость исходника %.1f' % src[y0:y1, x0:x1].mean())
