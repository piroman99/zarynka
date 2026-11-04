# -*- coding: utf-8 -*-
"""Проверка НА ЖИВОМ демо: надписи кадров лежат внутри плашек (не в углу).

Снимает страницы s5b и s5a прямо с piroman99.github.io и ищет пиксели цвета строки
внутри плашки — так же, как _ovl_inside.py, но по опубликованной сборке.
"""
import glob
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
BASE = 'https://piroman99.github.io/zarynka/vn2/index.html'
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

OUT = os.path.join(HERE, '.tmp_vo')
SCALE = 1280 / 2400.0
CASES = [('s5b', 0, (801, 690, 1599, 780), (0xff, 0xd2, 0x78)),
         ('s5a', 0, (1119, 505, 1848, 890), (0xf6, 0xee, 0xde)),
         ('s4', 0, (738, 684, 1644, 777), (0xf6, 0xee, 0xde))]

bad = 0
for nid, p, box, col in CASES:
    q = ('instant=1&auto=0&pause=1&pace=0&node=%d&page=%d&text=1&voice=0&music=0'
         % (node_index(nid), p))
    f = os.path.join(OUT, 'live_%s.png' % nid)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
                    '--disable-dev-shm-usage', '--hide-scrollbars',
                    '--window-size=1280,720', '--virtual-time-budget=9000',
                    '--screenshot=' + f, BASE + '?' + q],
                   capture_output=True, text=True, timeout=180)
    im = Image.open(f).convert('RGB')
    px = im.load()
    x0, y0 = int(box[0] * SCALE) + 3, int(box[1] * SCALE) + 3
    x1, y1 = int(box[2] * SCALE) - 3, int(box[3] * SCALE) - 3
    hits = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
            if all(abs(px[x, y][k] - col[k]) < 26 for k in range(3))]
    if not hits:
        print('%-4s стр.%d  НЕТ ТЕКСТА в плашке на живом демо' % (nid, p + 1))
        bad += 1
        continue
    hx0, hx1 = min(h[0] for h in hits), max(h[0] for h in hits)
    cx = (x0 + x1) / 2.0
    print('%-4s стр.%d  пикселей %5d  x %d..%d  центр %.1f vs ось плашки %.1f  %s'
          % (nid, p + 1, len(hits), hx0, hx1, (hx0 + hx1) / 2.0, cx,
             'OK' if abs((hx0 + hx1) / 2.0 - cx) < 10 else 'СМЕЩЁН'))
    if abs((hx0 + hx1) / 2.0 - cx) >= 10:
        bad += 1
print('\nпроблем на живом демо: %d' % bad)
sys.exit(1 if bad else 0)