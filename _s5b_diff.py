# -*- coding: utf-8 -*-
"""Точный диф живого демо кадра 12: снимок с титр-слоем и без (?ovl=0).
Разница = реальный bbox слоя в пространстве 2400x1350. Сверяем с заданным
(плашка 560..1360 x 830..920)."""
import os
import glob
import subprocess
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
OUT = os.path.join(HERE, '_sat')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

BASE = ('https://piroman99.github.io/zarynka/vn2/index.html'
        '?instant=1&auto=0&pause=1&pace=0&node=%d&page=0&text=1&voice=0&music=0'
        % node_index('s5b'))


def shot(extra, name):
    p = os.path.join(OUT, name)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=12000', '--screenshot=' + p, BASE + extra],
                   capture_output=True, text=True, timeout=180)
    return p


a = shot('', 's5b_on.png')
b = shot('&ovl=0', 's5b_off.png')
A = Image.open(a).convert('RGB')
B = Image.open(b).convert('RGB')
W, H = A.size
pa, pb = A.load(), B.load()
xs, ys = [], []
for y in range(H):
    for x in range(W):
        ra, ga, ba = pa[x, y]
        rb, gb, bb = pb[x, y]
        if abs(ra - rb) + abs(ga - gb) + abs(ba - bb) > 30:
            xs.append(x)
            ys.append(y)
k = 2400.0 / W
if xs:
    print('слой x %4.0f..%4.0f (центр %4.0f)  y %4.0f..%4.0f'
          % (min(xs) * k, max(xs) * k, (min(xs) + max(xs)) / 2 * k,
             min(ys) * k, max(ys) * k))
    print('задано плашка x 560..1360 (центр 960), y 830..920')
else:
    print('разницы нет — слой не отрисовался')
