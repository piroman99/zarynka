# -*- coding: utf-8 -*-
"""Точная проверка метки сцены: правый край чёрной плашки = последний тёмный пиксель
в её полосе (текст внутри полосы рвёт пробег, поэтому берём min/max, а не пробег).
Текст ищем только внутри плашки + 40 px запаса."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')


def is_dark(p):
    return p[0] < 30 and p[1] < 30 and p[2] < 30


def is_txt(p):
    return abs(p[0] - 232) <= 60 and abs(p[1] - 180) <= 60 and abs(p[2] - 120) <= 60


rows = []
for f in sorted(x for x in os.listdir(FIN) if x.endswith('.png')):
    im = Image.open(os.path.join(FIN, f)).convert('RGB')
    W, H = im.size
    k = W / 2400.0
    px = im.load()
    dark = []
    for y in range(int(50 * k), int(135 * k)):
        for x in range(int(40 * k), int(1400 * k)):
            if is_dark(px[x, y]):
                dark.append((x, y))
    if len(dark) < 500:
        rows.append((f, 'плашки нет', None, None, None))
        continue
    xs = [x for x, _ in dark]
    ys = [y for _, y in dark]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    # текст — только в полосе плашки, не правее x1+40
    tr = None
    for y in range(y0, y1 + 1):
        for x in range(x0, min(x1 + int(40 * k), int(1400 * k))):
            if is_txt(px[x, y]):
                if tr is None or x > tr:
                    tr = x
    if tr is None:
        rows.append((f, 'текста нет', (x0 / k, x1 / k), None, None))
        continue
    gap = (x1 - tr) / k
    rows.append((f, 'OK' if gap >= 1 else 'ОБРЕЗКА',
                 (x0 / k, x1 / k), tr / k, gap))

for f, st, plate, tr, gap in rows:
    if plate is None:
        print('%-8s %s' % (f, st))
    elif tr is None:
        print('%-8s плашка %.0f..%.0f  %s' % (f, plate[0], plate[1], st))
    else:
        print('%-8s плашка %4.0f..%4.0f  текст до %4.0f  запас %+5.1f px  %s'
              % (f, plate[0], plate[1], tr, gap, st))
