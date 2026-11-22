# -*- coding: utf-8 -*-
"""Ищем НАРИСОВАННУЮ скамейку в фоне alley: по цвету дерева (HSV) в левом низу.
Печатаем ASCII маски и координаты найденных пятен в пикселях фона и в долях кадра."""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'vn2', 'img', 'bg', 'alley.webp')

im = Image.open(P).convert('RGB')
W0, H0 = im.size
hsv = np.asarray(im.convert('HSV')).astype(np.int16)
H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
print('фон %dx%d' % (W0, H0))

# дерево: тёплый тон 8..40 градусов (PIL: 0..255 на 360) -> 6..28
wood = (H >= 6) & (H <= 30) & (S >= 45) & (V >= 45) & (V <= 205)
print('доля «дерева» в кадре: %.3f%%' % (100.0 * wood.mean()))


def ascii_mask(m, cols=96, rows=40, x0f=0.0, x1f=1.0, y0f=0.0, y1f=1.0):
    y0, y1 = int(y0f * m.shape[0]), int(y1f * m.shape[0])
    x0, x1 = int(x0f * m.shape[1]), int(x1f * m.shape[1])
    sub = m[y0:y1, x0:x1]
    h, w = sub.shape
    for r in range(rows):
        line = []
        for c in range(cols):
            a = sub[int(r * h / rows):int((r + 1) * h / rows),
                    int(c * w / cols):int((c + 1) * w / cols)]
            f = a.mean()
            line.append('#' if f > 0.5 else ('+' if f > 0.2 else ('.' if f > 0.05 else ' ')))
        print('|' + ''.join(line) + '|')


print('\n=== маска «дерево», весь кадр ===')
ascii_mask(wood, 96, 40)

# пятна: грубая разметка на уменьшенной маске
small = 320
m = np.asarray(Image.fromarray((wood * 255).astype(np.uint8))
               .resize((small, int(small * H0 / W0)), Image.BILINEAR)) > 127
lab = np.zeros(m.shape, np.int32)
cur = 0
comps = []
for yy in range(m.shape[0]):
    for xx in range(m.shape[1]):
        if m[yy, xx] and lab[yy, xx] == 0:
            cur += 1
            stack = [(yy, xx)]
            lab[yy, xx] = cur
            pts = []
            while stack:
                a, b = stack.pop()
                pts.append((a, b))
                for da in (-1, 0, 1):
                    for db in (-1, 0, 1):
                        na, nb = a + da, b + db
                        if 0 <= na < m.shape[0] and 0 <= nb < m.shape[1] \
                                and m[na, nb] and lab[na, nb] == 0:
                            lab[na, nb] = cur
                            stack.append((na, nb))
            comps.append(pts)

comps.sort(key=len, reverse=True)
sc = W0 / float(small)
print('\n=== пятна «дерева» (топ-8) ===')
for pts in comps[:8]:
    ys = [p[0] for p in pts]
    xs = [p[1] for p in pts]
    if len(pts) < 40:
        break
    print('точек %5d  bbox x %.1f%%..%.1f%%  y %.1f%%..%.1f%%  (px %d..%d / %d..%d)'
          % (len(pts), 100.0 * min(xs) / small, 100.0 * max(xs) / small,
             100.0 * min(ys) / m.shape[0], 100.0 * max(ys) / m.shape[0],
             min(xs) * sc, max(xs) * sc, min(ys) * sc, max(ys) * sc))
