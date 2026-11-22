# -*- coding: utf-8 -*-
"""Разворот пропа-скамейки: где спинка, куда смотрит сиденье, куда наклонена верхняя рейка.

Никакого зрения: берём альфу `vn2/img/prop/bench.webp` и считаем по колонкам верхнюю
кромку (верх спинки), по строкам — левую/правую границы, и отдельно сравниваем размах
спинки (верхние 45 % высоты) и сиденья (низ).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')

im = Image.open(P).convert('RGBA')
a = np.asarray(im.split()[-1]).astype(np.float32)
h, w = a.shape
m = a > 90
print('проп %dx%d, плотных пикселей %.1f%%' % (w, h, 100.0 * m.mean()))

ys, xs = np.nonzero(m)
print('bbox: x %d..%d  y %d..%d' % (xs.min(), xs.max(), ys.min(), ys.max()))

# верхняя кромка по колонкам (в средней трети, где спинка точно есть)
tops = []
for x in range(int(0.05 * w), int(0.95 * w)):
    col = np.nonzero(m[:, x])[0]
    if len(col):
        tops.append((x, col.min()))
tops = np.array(tops, float)
if len(tops) > 20:
    k, b = np.polyfit(tops[:, 0], tops[:, 1], 1)
    print('верхняя кромка: y = %.4f x + %.1f -> наклон %.1f° (плюс = вниз-вправо)'
          % (k, b, np.degrees(np.arctan(k))))

# низ по колонкам (ножки/тень)
bots = []
for x in range(int(0.05 * w), int(0.95 * w)):
    col = np.nonzero(m[:, x])[0]
    if len(col):
        bots.append((x, col.max()))
bots = np.array(bots, float)
if len(bots) > 20:
    k2, b2 = np.polyfit(bots[:, 0], bots[:, 1], 1)
    print('нижняя кромка: y = %.4f x + %.1f -> наклон %.1f°' % (k2, b2, np.degrees(np.arctan(k2))))

# размах спинки (верх 45 %) и сиденья (55..85 %)
def span(y0f, y1f, label):
    sub = m[int(y0f * h):int(y1f * h)]
    cols = np.nonzero(sub.any(0))[0]
    rows = np.nonzero(sub.any(1))[0]
    print('  %-8s: x %d..%d (размах %d px = %.0f%% ширины), заполнено %.0f%%'
          % (label, cols.min(), cols.max(), cols.max() - cols.min(),
             100.0 * (cols.max() - cols.min()) / w, 100.0 * sub.mean()))


print('полосы по высоте:')
span(0.00, 0.45, 'спинка')
span(0.45, 0.62, 'сиденье')
span(0.62, 1.00, 'ножки')

# профиль заполнения по строкам — где просвет под сиденьем
print('\nзаполнение по строкам (10 полос):')
for i in range(10):
    y0, y1 = int(i * h / 10), int((i + 1) * h / 10)
    print('  %3d..%3d%%  %5.1f%%' % (100 * y0 // h, 100 * y1 // h, 100.0 * m[y0:y1].mean()))

# ASCII силуэт 60x18
print('\nсилуэт:')
for r in range(18):
    y0, y1 = int(r * h / 18), int((r + 1) * h / 18)
    line = []
    for c in range(60):
        x0, x1 = int(c * w / 60), int((c + 1) * w / 60)
        f = m[y0:y1, x0:x1].mean()
        line.append('#' if f > 0.6 else ('+' if f > 0.25 else ('.' if f > 0.06 else ' ')))
    print('|' + ''.join(line) + '|')
