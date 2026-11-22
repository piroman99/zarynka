# -*- coding: utf-8 -*-
"""Проверить, что на странице s1[0] реально стоит кадр СТЕНЫ, а не пусто/подворотня.

    python3 _check_s1_bg.py

Считает:
  * какие URL картинок запросил предзагрузчик/сцена (по логу сети — через 404-пробу);
  * среднюю яркость и «тёмную долю» снятого кадра страницы 1 и 2 — у подворотни
    (ночной двор) доля тёмных пикселей заметно выше, чем у стены днём;
  * корреляцию скриншота с финальным кадром s1a.png / s1.png по уменьшенной сетке.
Печатает вердикт: совпал ли фон страницы 1 с финальным кадром стены.
"""
import os
import numpy as np
from PIL import Image

S = '_sat'
FIN = os.path.join('assets', 'final', 'prolog')


def small(p, n=96):
    im = Image.open(p).convert('L').resize((n, n), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    return a


def corr(a, b):
    a = a.ravel() - a.mean()
    b = b.ravel() - b.mean()
    d = (np.sqrt((a * a).sum()) * np.sqrt((b * b).sum())) or 1
    return float((a * b).sum() / d)


def dark_frac(p):
    a = np.asarray(Image.open(p).convert('L'), np.float32)
    return float((a < 60).mean()), float(a.mean())


shots = [('s1_p0_wall', 's1a'), ('s1_p1_alley', 's1'), ('p6_p0', 'p6'), ('p6_p1', 'p6')]
for name, fin in shots:
    sp = os.path.join(S, name + '.png')
    fp = os.path.join(FIN, fin + '.png')
    if not os.path.exists(sp):
        print('нет скриншота', sp)
        continue
    d, m = dark_frac(sp)
    c = corr(small(sp), small(fp)) if os.path.exists(fp) else float('nan')
    print('%-12s фон %-4s  тёмных=%.2f средняя=%.0f  корреляция=%.3f'
          % (name, fin, d, m, c))

print('\nвердикт s1[0]: скриншот должен коррелировать со s1a (стена) сильнее, чем с s1')
a0 = small(os.path.join(S, 's1_p0_wall.png'))
if os.path.exists(os.path.join(FIN, 's1a.png')):
    ca, cb = corr(a0, small(os.path.join(FIN, 's1a.png'))), corr(a0, small(os.path.join(FIN, 's1.png')))
    print('  s1a=%.3f  s1=%.3f  ->  %s' % (ca, cb, 'СТЕНА' if ca > cb else 'ПОДВОРОТНЯ (ошибка)'))
