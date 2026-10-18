# -*- coding: utf-8 -*-
"""Проверка: (1) фон логотипов по углам, (2) какие источники в тизере вертикальные,
(3) есть ли готовые 16:9 кадры с Екатериной в комбинезоне."""
import os, glob
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))

print('--- углы логотипов (r,g,b)')
for rel in ['assets/gen/logo_a_0.jpg', 'assets/gen/logo_b_0.jpg',
            'assets/gen/logo_c_0.jpg', 'vn2/img/logo.png']:
    im = Image.open(os.path.join(HERE, rel)).convert('RGB')
    w, h = im.size
    pts = {'TL': (2, 2), 'TR': (w - 3, 2), 'BL': (2, h - 3), 'BR': (w - 3, h - 3),
           'center-top': (w // 2, 2)}
    print('%-32s %s' % (rel, {k: im.getpixel(v) for k, v in pts.items()}))

print('\n--- соотношения источников тизера')
for rel in ['assets/gen/ok_space_station_0.jpg', 'assets/gen/ok_reception_fix2_0.jpg',
            'assets/gen/ok_x_kate_moon_0.jpg']:
    im = Image.open(os.path.join(HERE, rel))
    print('%-40s %sx%s  %.3f  %s' % (rel, im.size[0], im.size[1],
                                     im.size[0] / im.size[1], 'ВЕРТИКАЛЬНЫЙ' if im.size[0] < im.size[1] else '16:9/landscape'))

print('\n--- кандидаты «Кейт в комбинезоне» (все картинки ассетов)')
best = []
for ext in ('*.jpg', '*.png', '*.webp'):
    for p in glob.glob(os.path.join(HERE, 'assets', '**', ext), recursive=True):
        n = os.path.basename(p).lower()
        if 'kate' not in n and 'kat' not in n:
            continue
        try:
            im = Image.open(p)
        except Exception:
            continue
        best.append((round(im.size[0] / im.size[1], 3), im.size, os.path.relpath(p, HERE)))
for a, s, p in sorted(best, key=lambda t: -t[0])[:40]:
    print('  %.3f %10s %s' % (a, 'x'.join(map(str, s)), p))
