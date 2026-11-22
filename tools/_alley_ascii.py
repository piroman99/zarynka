# -*- coding: utf-8 -*-
"""ASCII-карта фона аллеи: яркость + зелень, чтобы понять композицию (дорожка, ели, ворота).

Плюс профиль «где край дорожки» по колонкам: сканируем снизу вверх, ищем переход
светлое (дорожка) → тёмное (земля/трава), и подгоняем линию.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
p = os.path.join(ROOT, 'vn2', 'img', 'bg', 'alley.webp')
im = Image.open(p).convert('RGB')
W0, H0 = im.size
print('фон:', W0, 'x', H0)

small = 400
sm = im.resize((small, int(small * H0 / W0)), Image.LANCZOS)
rgb = np.asarray(sm).astype(np.float32)
H, W = rgb.shape[:2]
lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
mx = rgb.max(2)
mn = rgb.min(2)
sat = (mx - mn) / (mx + 1e-6)
green = (sat > 0.15) & (rgb[..., 1] >= rgb[..., 0]) & (rgb[..., 1] >= rgb[..., 2])

cols, rows = 78, 30
shade = ' .:-=+*#%@'
print('\n--- яркость (светлое = @) ---')
for r in range(rows):
    y0, y1 = int(r * H / rows), int((r + 1) * H / rows)
    line = ''
    for c in range(cols):
        x0, x1 = int(c * W / cols), int((c + 1) * W / cols)
        v = lum[y0:y1, x0:x1].mean()
        g = green[y0:y1, x0:x1].mean()
        ch = shade[min(9, int(v / 25.6))]
        if g > 0.45 and v < 150:
            ch = 'G'
        line += ch
    print('|' + line + '|')

print('\n--- зелень (G) ---')
for r in range(rows):
    y0, y1 = int(r * H / rows), int((r + 1) * H / rows)
    line = ''
    for c in range(cols):
        x0, x1 = int(c * W / cols), int((c + 1) * W / cols)
        g = green[y0:y1, x0:x1].mean()
        line += 'G' if g > 0.6 else ('g' if g > 0.3 else ('+' if g > 0.12 else '.'))
    print('|' + line + '|')

# --- край дорожки: снизу вверх ищем переход светлое->тёмное в нижней половине ---
print('\n--- профиль края дорожки (x%%: y в %% высоты, где светлое кончается) ---')
pts = []
for c in range(2, cols - 2):
    x0, x1 = int(c * W / cols), int((c + 1) * W / cols)
    col = lum[int(0.45 * H):, x0:x1].mean(1)
    # идём снизу вверх: пока светло — это дорожка; как только темнее порога — край
    thr = np.percentile(col, 55)
    y_edge = None
    for i in range(len(col) - 1, -1, -1):
        if col[i] < thr - 6:
            y_edge = int(0.45 * H) + i
            break
    if y_edge is None:
        continue
    pts.append((c, y_edge / H))
    print('  x=%2d%%  y=%3.0f%%' % (int(100.0 * c / cols), 100.0 * y_edge / H))

if len(pts) > 8:
    xs = np.array([q[0] for q in pts], np.float64)
    ys = np.array([q[1] for q in pts], np.float64)
    # робастная подгонка: 3 прохода с отбраковкой выбросов
    keep = np.ones(len(xs), bool)
    for _ in range(3):
        k, b = np.polyfit(xs[keep], ys[keep], 1)
        res = np.abs(ys - (k * xs + b))
        keep = res < max(0.02, 2.0 * res[keep].mean())
    print('линия края: y = %.5f*x + %.4f  → угол %.2f° к горизонту (по %d точкам)'
          % (k, b, np.degrees(np.arctan(k * (H / W))), keep.sum()))
