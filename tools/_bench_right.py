# -*- coding: utf-8 -*-
"""Почему у скамейки «растворяется» правый конец и нет правой передней ножки.

Сравниваем два файла: исходник `assets/sprites/prop_bench.png` (полное разрешение)
и то, что уходит в игру `vn2/img/prop/bench.webp`. Печатаем по колонкам:
  • верх и низ маски (где кончается рисунок),
  • среднюю непрозрачность (где «растворяется» — альфа падает),
  • вертикальные прогоны в нижней трети — это ножки.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
FILES = [
    ('исходник', os.path.join(ROOT, 'assets', 'sprites', 'prop_bench.png')),
    ('в игре', os.path.join(ROOT, 'vn2', 'img', 'prop', 'bench.webp')),
]

for label, p in FILES:
    im = Image.open(p).convert('RGBA')
    a = np.asarray(im)
    alpha = a[:, :, 3].astype(np.float32)
    Hf, Wf = alpha.shape
    print('\n=== %s: %s %dx%d' % (label, os.path.basename(p), Wf, Hf))
    m = alpha > 140
    ys, xs = np.nonzero(m)
    print('маска: x %d..%d, y %d..%d' % (xs.min(), xs.max(), ys.min(), ys.max()))
    print('средняя альфа по всему файлу: %.1f' % alpha.mean())
    print('\n x%%   x    верх   низ   ср.альфа  покрытие  ножек(прогонов в нижней трети)')
    for frac in np.arange(0.02, 1.0, 0.04):
        x = int(frac * Wf)
        col_a = alpha[:, x]
        col_m = m[:, x]
        if col_m.sum() == 0:
            print(' %3.0f %4d      -     -      %5.1f      0%%    -' % (frac * 100, x, col_a.mean()))
            continue
        idx = np.nonzero(col_m)[0]
        # прогоны в нижней трети (ножки)
        y0 = int(Hf * 0.66)
        low = col_m[y0:]
        runs = 0
        prev = False
        for v in low:
            if v and not prev:
                runs += 1
            prev = v
        print(' %3.0f %4d   %4d  %4d     %5.1f    %3.0f%%    %d'
              % (frac * 100, x, idx.min(), idx.max(), col_a.mean(), 100.0 * col_m.mean(), runs))

    # где альфа «полусирая» — там рисунок тает
    soft = ((alpha > 20) & (alpha < 160))
    print('\nполупрозрачных пикселей (20<альфа<160): %.1f%% файла' % (100.0 * soft.mean()))
    # распределение по 8 вертикальным полосам
    print('по полосам (доля полупрозрачных):')
    for i in range(8):
        x0, x1 = int(Wf * i / 8), int(Wf * (i + 1) / 8)
        print('  x %4d..%4d: %4.1f%%' % (x0, x1, 100.0 * soft[:, x0:x1].mean()))
