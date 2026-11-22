# -*- coding: utf-8 -*-
"""Проверка «p6 пополам»: стр. 1 марсианская, стр. 2 лунная — числами.

    python3 _check_p6_split.py

Для скриншотов `_sat/p6_p0.png` / `p6_p1.png` печатает долю охры (красно-оранжевых
пикселей), средний цвет и корреляцию с обоими финальными кадрами (p6.png = Марс,
p6luna.png = лунная база).
"""
import os
import numpy as np
from PIL import Image

S = '_sat'
FIN = os.path.join('assets', 'final', 'prolog')


def small(p, n=96):
    return np.asarray(Image.open(p).convert('L').resize((n, n), Image.LANCZOS), np.float32)


def corr(a, b):
    a = a.ravel() - a.mean()
    b = b.ravel() - b.mean()
    return float((a * b).sum() / ((np.sqrt((a * a).sum()) * np.sqrt((b * b).sum())) or 1))


def ochre(p):
    a = np.asarray(Image.open(p).convert('RGB'), np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return float(((r > 95) & (r > g + 18) & (g > b + 10) & (r - b > 40)).mean())


for name, want in (('p6_p0', 'p6'), ('p6_p1', 'p6luna')):
    sp = os.path.join(S, name + '.png')
    if not os.path.exists(sp):
        print('нет', sp)
        continue
    a = np.asarray(Image.open(sp).convert('RGB'), np.float32)
    c_mars = corr(small(sp), small(os.path.join(FIN, 'p6.png')))
    c_luna = corr(small(sp), small(os.path.join(FIN, 'p6luna.png')))
    verdict = 'МАРС' if c_mars > c_luna else 'ЛУНА'
    print('%-6s охра=%.3f mean=%s  corr(Марс)=%.3f corr(Луна)=%.3f -> %s (ждали %s) %s'
          % (name, ochre(sp), tuple(round(float(x), 1) for x in a.reshape(-1, 3).mean(0)),
             c_mars, c_luna, verdict,
             'МАРС' if want == 'p6' else 'ЛУНА',
             'OK' if (verdict == ('МАРС' if want == 'p6' else 'ЛУНА')) else 'FAIL'))
