# -*- coding: utf-8 -*-
"""Эталон угла: НАРИСОВАННАЯ в фоне скамейка (левый низ alley_b_0.jpg, до затирания).

Она нарисована генератором в перспективе этой же аллеи — значит её длинная ось и есть
правильный угол для скамейки в этом кадре. Считаем: верхнюю кромку по колонкам,
нижнюю кромку, PCA маски и отношение «высота у ближнего торца / у дальнего».
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'assets', 'gen', 'alley_b_0.jpg')
im = Image.open(P).convert('RGB')
W, H = im.size
hsv = np.asarray(im.convert('HSV')).astype(np.int16)
Hc, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
wood = (Hc >= 6) & (Hc <= 32) & (S >= 55) & (V >= 45) & (V <= 210)
print('фон %dx%d' % (W, H))

# окно вокруг пятна (по замеру на клиенте 1920x1080 -> в исходнике 1672x941)
X0, X1, Y0, Y1 = 0, 260, 720, 880
sub = wood[Y0:Y1, X0:X1]
print('окно x %d..%d y %d..%d, дерево %.1f%%' % (X0, X1, Y0, Y1, 100 * sub.mean()))

cols, rows = 84, 26
print('\nмаска «дерево» в окне:')
for r in range(rows):
    line = []
    for c in range(cols):
        ya, yb = int(r * sub.shape[0] / rows), int((r + 1) * sub.shape[0] / rows)
        xa, xb = int(c * sub.shape[1] / cols), int((c + 1) * sub.shape[1] / cols)
        f = sub[ya:yb, xa:xb].mean()
        line.append('#' if f > 0.5 else ('+' if f > 0.2 else ('.' if f > 0.05 else ' ')))
    print('|' + ''.join(line) + '| y=%d' % (Y0 + int(r * sub.shape[0] / rows)))

ys, xs = np.nonzero(sub)
print('\nbbox: x %d..%d y %d..%d' % (X0 + xs.min(), X0 + xs.max(),
                                     Y0 + ys.min(), Y0 + ys.max()))

# верхняя и нижняя кромки по колонкам (только там, где столбец не пустой)
tops, bots, colsx = [], [], []
for x in range(sub.shape[1]):
    col = np.nonzero(sub[:, x])[0]
    if len(col) >= 3:
        colsx.append(x)
        tops.append(col.min())
        bots.append(col.max())
colsx = np.array(colsx, float)
tops = np.array(tops, float)
bots = np.array(bots, float)
if len(colsx) > 20:
    kt, bt = np.polyfit(colsx, tops, 1)
    kb, bb = np.polyfit(colsx, bots, 1)
    print('верхняя кромка: наклон %+.1f° (плюс = вниз-вправо)' % np.degrees(np.arctan(kt)))
    print('нижняя кромка : наклон %+.1f°' % np.degrees(np.arctan(kb)))
    # высота у левого и правого края пятна
    for frac in (0.05, 0.5, 0.95):
        x = int(colsx.min() + frac * (colsx.max() - colsx.min()))
        print('  x=%3d: верх %.0f, низ %.0f, высота %.0f px'
              % (X0 + x, kt * x + bt, kb * x + bb, (kb * x + bb) - (kt * x + bt)))

# PCA маски
pts = np.stack([xs, ys], 1).astype(np.float64)
c = pts.mean(0)
cov = np.cov((pts - c).T)
w, v = np.linalg.eigh(cov)
main = v[:, np.argmax(w)]
ang = np.degrees(np.arctan2(main[1], main[0]))
if ang > 90:
    ang -= 180
if ang < -90:
    ang += 180
print('\nPCA длинной оси пятна: %+.1f° (0 = горизонтально, минус = вверх-вправо)' % ang)
