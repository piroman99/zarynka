# -*- coding: utf-8 -*-
"""Числовая проверка метки: находит чёрную плашку в левом верхнем углу и проверяет,
что текст метки (232,180,120) не выходит за её правый край."""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FIN = os.path.join(HERE, 'assets', 'final', 'prolog')
TXT = (232, 180, 120)


def close(p, c, tol=40):
    return all(abs(p[i] - c[i]) <= tol for i in range(3))


for f in sorted(x for x in os.listdir(FIN) if x.endswith('.png')):
    im = Image.open(os.path.join(FIN, f)).convert('RGB')
    W, H = im.size
    k = W / 2400.0
    px = im.load()
    y0, y1 = int(60 * k), int(140 * k)
    xmax = int(1200 * k)
    dark = []
    text = []
    for y in range(y0, y1):
        for x in range(int(40 * k), xmax):
            p = px[x, y]
            if p[0] < 26 and p[1] < 26 and p[2] < 26:
                dark.append((x, y))
            elif close(p, TXT, 45):
                text.append((x, y))
    if not dark or not text:
        print('%-8s плашка=%s текст=%s  — пропуск' % (f, bool(dark), bool(text)))
        continue
    right = max(x for x, _ in dark)
    tright = max(x for x, _ in text)
    over = (tright - right) / k
    print('%-8s плашка до x=%.0f, текст до x=%.0f, вылет=%+.1f px  %s'
          % (f, right / k, tright / k, over, 'OK' if over <= 1 else 'ОБРЕЗКА'))
