# -*- coding: utf-8 -*-
"""Настоящий Hough: под каким углом идут длинные прямые (край дорожки/бордюр) на фоне.

Для каждого угла θ считаем rho = x·cosθ + y·sinθ, строим гистограмму rho по точкам
сильных градиентов; длина самой длинной прямой при этом θ = максимум гистограммы.
Печатаем топ-углы и для контроля — ту же процедуру по пропу-скамейке (её длинная ось).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))



ROOT = os.path.dirname(HERE)
def hough_angles(path, x0f=0.0, x1f=1.0, y0f=0.0, y1f=1.0, small=600,
                 thresh_pct=92, label=''):
    im = Image.open(path).convert('L')
    W0, H0 = im.size
    sc = small / float(W0)
    im = im.resize((small, max(1, int(H0 * sc))), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    H, W = a.shape
    gx = np.zeros_like(a)
    gy = np.zeros_like(a)
    gx[:, 1:-1] = (a[:, 2:] - a[:, :-2]) * 0.5
    gy[1:-1, :] = (a[2:, :] - a[:-2, :]) * 0.5
    mag = np.hypot(gx, gy)
    x0, x1 = int(x0f * W), int(x1f * W)
    y0, y1 = int(y0f * H), int(y1f * H)
    sub = mag[y0:y1, x0:x1]
    thr = np.percentile(sub, thresh_pct)
    ys, xs = np.nonzero(sub >= max(thr, 1e-6))
    if len(xs) < 50:
        print('%s: мало градиентов (%d)' % (label, len(xs)))
        return None
    xs = xs.astype(np.float64)
    ys = ys.astype(np.float64)
    best = []
    for deg in np.arange(-25.0, 25.001, 0.25):
        th = np.radians(deg)
        rho = xs * np.cos(th) + ys * np.sin(th)
        hist, edges = np.histogram(rho, bins=max(60, int(sub.shape[1] * 0.5)))
        i = int(np.argmax(hist))
        best.append((hist[i], deg, 0.5 * (edges[i] + edges[i + 1])))
    best.sort(reverse=True)
    print('\n%s  [%s, x %.0f..%.0f%% y %.0f..%.0f%%, %d точек]'
          % (label, os.path.basename(path), x0f * 100, x1f * 100, y0f * 100, y1f * 100, len(xs)))
    seen = []
    for cnt, deg, rho in best:
        if any(abs(deg - d) < 1.5 for d in seen):
            continue
        seen.append(deg)
        print('   %6.2f°  rho %7.1f  точек на прямой: %d' % (deg, rho, cnt))
        if len(seen) >= 5:
            break
    return best[0][1]


bg = os.path.join(ROOT, 'vn2', 'img', 'bg', 'alley.webp')
prop = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')

a1 = hough_angles(bg, 0.00, 0.45, 0.55, 1.00, label='ФОН: левый низ (край дорожки у скамейки)')
a2 = hough_angles(bg, 0.35, 0.95, 0.30, 0.90, label='ФОН: центр-право (дорожка к воротам)')
a3 = hough_angles(bg, 0.00, 1.00, 0.40, 1.00, label='ФОН: весь нижний пояс')
p1 = hough_angles(prop, 0.0, 1.0, 0.0, 1.0, label='ПРОП-СКАМЕЙКА (вся)')
p2 = hough_angles(prop, 0.0, 1.0, 0.0, 0.45, label='ПРОП-СКАМЕЙКА (спинка)')
print('\nуглы: дорожка слева %s, центр %s, пояс %s; скамейка %s / спинка %s'
      % (a1, a2, a3, p1, p2))
