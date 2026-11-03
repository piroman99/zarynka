# -*- coding: utf-8 -*-
"""Точная проверка метки сцены: ищем чёрную плашку в строке y=70..128 (пространство 2400)
и проверяем, что текст (232,180,120) не выходит за её правый край.
Ищем ТОЛЬКО внутри полосы плашки, чтобы не ловить оранжевые пиксели сцены."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')


def is_dark(p):
    return p[0] < 26 and p[1] < 26 and p[2] < 26


def is_txt(p):
    return (abs(p[0] - 232) <= 55 and abs(p[1] - 180) <= 55 and abs(p[2] - 120) <= 55)


for f in sorted(x for x in os.listdir(FIN) if x.endswith('.png')):
    im = Image.open(os.path.join(FIN, f)).convert('RGB')
    W, H = im.size
    k = W / 2400.0
    px = im.load()
    ymid = int(99 * k)                      # середина плашки (70..128)
    # правый край плашки — самый длинный тёмный пробег в этой строке
    best = (0, 0, 0)
    x = int(60 * k)
    while x < int(1400 * k):
        if is_dark(px[x, ymid]):
            s = x
            while x < int(1400 * k) and is_dark(px[x, ymid]):
                x += 1
            if x - s > best[2]:
                best = (s, x - 1, x - s)
        else:
            x += 1
    if best[2] < int(100 * k):
        print('%-8s плашки нет (пробег %d px)' % (f, best[2]))
        continue
    p0, p1 = best[0], best[1]
    tright = None
    for y in range(int(76 * k), int(124 * k)):
        for xx in range(p0, min(p1 + int(80 * k), int(1400 * k))):
            if is_txt(px[xx, y]):
                if tright is None or xx > tright:
                    tright = xx
    if tright is None:
        print('%-8s плашка %d..%d, текста не нашли' % (f, p0 / k, p1 / k))
        continue
    over = (tright - p1) / k
    print('%-8s плашка %4.0f..%4.0f  текст до %4.0f  запас %+5.1f px  %s'
          % (f, p0 / k, p1 / k, tright / k, -over, 'OK' if over <= 1 else 'ОБРЕЗКА'))
