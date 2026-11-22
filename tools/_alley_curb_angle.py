# -*- coding: utf-8 -*-
"""Под каким углом идут БОРДЮР/край дорожки на фоне аллеи и под каким — скамейка.

Скамейка должна стоять ровно к бордюру: значит её длинная ось и линия края дорожки
должны быть параллельны (в перспективе — сходиться в ту же точку схода).

Метод: простой Hough по градиенту яркости — для каждого угла суммируем |grad| вдоль
линий этого направления в нижней части кадра (где дорожка и бордюр). Плюс отдельно
угол оси пропа-скамейки (PCA по плотной альфе).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))



ROOT = os.path.dirname(HERE)
def hough(path, x0f, x1f, y0f, y1f, label, small=480):
    im = Image.open(path).convert('L')
    W0, H0 = im.size
    im = im.resize((small, int(small * H0 / W0)), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    a = (a - a.mean()) / (a.std() + 1e-6)
    H, W = a.shape
    gx = np.zeros_like(a)
    gy = np.zeros_like(a)
    gx[:, 1:-1] = (a[:, 2:] - a[:, :-2]) * 0.5
    gy[1:-1, :] = (a[2:, :] - a[:-2, :]) * 0.5
    mag = np.hypot(gx, gy)
    # область интереса
    xs = slice(int(x0f * W), int(x1f * W))
    ys = slice(int(y0f * H), int(y1f * H))
    roi = mag[ys, xs]
    rh, rw = roi.shape

    best = []
    for deg in np.arange(-25.0, 25.01, 0.5):
        th = np.radians(deg)
        dx, dy = np.cos(th), np.sin(th)
        acc = np.zeros_like(roi)
        for off in range(-30, 31, 2):
            sx = int(round(off * dx))
            sy = int(round(off * dy))
            if abs(sy) < rh and abs(sx) < rw:
                acc += np.roll(np.roll(roi, sy, axis=0), sx, axis=1)
        best.append((acc.sum() / acc.size, deg))
    best.sort(reverse=True)
    print('\n%s  (%s, область x %.0f..%.0f%% y %.0f..%.0f%%)'
          % (label, os.path.basename(path), x0f * 100, x1f * 100, y0f * 100, y1f * 100))
    for score, deg in best[:6]:
        print('   %6.1f°  score %.4f' % (deg, score))
    return best[0][1]


def bench_axis(path):
    a = np.asarray(Image.open(path).split()[-1]).astype(np.float32)
    m = a > 90
    ys, xs = np.nonzero(m)
    pts = np.stack([xs.astype(np.float64), ys.astype(np.float64)], 1)
    c = pts.mean(0)
    w, v = np.linalg.eigh(np.cov((pts - c).T))
    main = v[:, np.argmax(w)]
    ang = np.degrees(np.arctan2(main[1], main[0]))
    if ang > 90:
        ang -= 180
    if ang < -90:
        ang += 180
    return ang


bg = os.path.join(ROOT, 'vn2', 'img', 'bg', 'alley.webp')
prop = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')

# дорожка уходит в глубину к воротам (центр-право), скамейка слева на переднем плане:
# край дорожки ищем в левой/центральной нижней части кадра
c1 = hough(bg, 0.02, 0.55, 0.45, 0.95, 'край дорожки (левая часть, под скамейкой)')
c2 = hough(bg, 0.30, 0.85, 0.35, 0.85, 'край дорожки (центр → ворота)')
c3 = hough(bg, 0.02, 0.98, 0.30, 0.95, 'весь нижний пояс кадра')

b = bench_axis(prop)
print('\nось пропа-скамейки (PCA): %.2f°' % b)
print('\nразница скамейка − дорожка: %.2f° (левая) / %.2f° (центр) / %.2f° (весь пояс)'
      % (b - c1, b - c2, b - c3))
print('ноль = скамейка ровно к бордюру.')
