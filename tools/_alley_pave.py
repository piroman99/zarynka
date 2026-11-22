# -*- coding: utf-8 -*-
"""Геометрия фона аллеи: где тротуар/асфальт и под каким углом он уходит в глубину.

Глаз у меня нет, поэтому считаю:
  1) ASCII-карту яркости кадра — общая композиция (где тёмные ели, где светлый асфальт);
  2) Hough по градиентам в нижней половине — длинные линии (бордюр, край асфальта,
     кромка тротуара), их углы и точки пересечения с горизонтом (точка схода);
  3) профиль «дорожного» цвета по строкам — где кадр светлый и ровный (асфальт).

Печатает: угол самой длинной линии, её положение, оценку точки схода.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
BG = os.path.join(ROOT, 'assets', 'gen', 'alley_b_nobench__gpt-image-2_0.png')

im = Image.open(BG).convert('RGB').resize((836, 470), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
g = a.mean(axis=2)
H, W = g.shape
print('рабочий размер', W, H)

# ---------------- 1. ASCII-карта: 64x32 блока, символ = яркость
bx, by = W // 64, H // 32
chars = ' .:-=+*#%@'
print('\nASCII (светлое = @, тёмное = пробел), 64 колонки:')
for j in range(32):
    row = ''
    for i in range(64):
        blk = g[j * by:(j + 1) * by, i * bx:(i + 1) * bx]
        v = blk.mean() / 255.0
        row += chars[min(len(chars) - 1, int(v * len(chars)))]
    print('%02d %s' % (j, row))

# ---------------- 2. градиенты + Hough в нижних 55 %
lower = g[int(H * 0.45):, :]
gy, gx = np.gradient(lower)
mag = np.hypot(gx, gy)
thr = np.percentile(mag, 97.5)
ys, xs = np.nonzero(mag > thr)
xs = xs.astype(np.float64)
ys = ys.astype(np.float64) + int(H * 0.45)
print('\nточек для Hough:', len(xs), 'порог', round(float(thr), 1))

thetas = np.deg2rad(np.arange(0, 180, 1.0))
ct, st = np.cos(thetas), np.sin(thetas)
diag = int(np.hypot(W, H)) + 1
acc = np.zeros((len(thetas), 2 * diag), dtype=np.int32)
# прореживаем, чтобы не ждать
sel = np.arange(0, len(xs), max(1, len(xs) // 20000))
for k in sel:
    rho = xs[k] * ct + ys[k] * st
    ri = np.round(rho).astype(int) + diag
    acc[np.arange(len(thetas)), ri] += 1

flat = np.argsort(acc.ravel())[::-1][:4000]
picked = []
for f in flat:
    t_i, r_i = np.unravel_index(f, acc.shape)
    th = np.rad2deg(thetas[t_i])
    rho = r_i - diag
    # угол линии в экранных координатах (y вниз): направление вдоль линии
    # нормаль (cos,sin) -> направление линии (-sin, cos); наклон в градусах от горизонтали
    ang = np.rad2deg(np.arctan2(ct[t_i], -st[t_i]))
    if not any(abs(th - p[0]) < 3 and abs(rho - p[1]) < 14 for p in picked):
        picked.append((th, rho, int(acc[t_i, r_i]), ang))
    if len(picked) >= 14:
        break

print('\nтоп линий (theta=нормаль, rho, голоса, наклон линии от горизонтали):')
for th, rho, v, ang in picked:
    print('  theta %5.1f  rho %6.1f  votes %4d  наклон %+7.1f°' % (th, rho, v, ang))

# ---------------- 3. пересечения сильных линий = точка схода
good = [p for p in picked if p[2] > picked[0][2] * 0.35][:8]
print('\nсильных линий для точки схода:', len(good))
cross = []
for i in range(len(good)):
    for j in range(i + 1, len(good)):
        t1, r1 = np.deg2rad(good[i][0]), good[i][1]
        t2, r2 = np.deg2rad(good[j][0]), good[j][1]
        det = np.cos(t1) * np.sin(t2) - np.cos(t2) * np.sin(t1)
        if abs(det) < 0.15:
            continue
        x = (r1 * np.sin(t2) - r2 * np.sin(t1)) / det
        y = (r2 * np.cos(t1) - r1 * np.cos(t2)) / det
        if 0 <= x <= W and -0.2 * H <= y <= H:
            cross.append((x, y))
if cross:
    cx = float(np.median([c[0] for c in cross]))
    cy = float(np.median([c[1] for c in cross]))
    print('точка схода ~ x=%.0f y=%.0f (медиана %d пересечений)' % (cx, cy, len(cross)))
    print('в долях кадра: x %.2f, y %.2f' % (cx / W, cy / H))

# ---------------- 4. где асфальт: цветовые полосы внизу
print('\nсредний цвет по вертикальным третям нижней половины (RGB 0..255):')
for j, name in enumerate(['низ', 'ниже центра', 'центр']):
    y0 = int(H * (0.95 - 0.15 * j))
    band = a[y0 - 10:y0, :, :]
    for i, nm in enumerate(['левая', 'центр', 'правая']):
        x0, x1 = int(W * (0.02 + 0.33 * i)), int(W * (0.02 + 0.33 * i) + W * 0.28)
        c = band[:, x0:x1].reshape(-1, 3).mean(axis=0)
        print('  %-12s %-7s y=%3d  R %3.0f G %3.0f B %3.0f  ярк %3.0f'
              % (name, nm, y0, c[0], c[1], c[2], c.mean()))
