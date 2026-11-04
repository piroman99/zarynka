# -*- coding: utf-8 -*-
"""Живое демо: строка надписи ждёт свою фразу (?ovlp=P = прогресс страницы).

Снимаем опубликованную сборку на P=0.05 / 0.50 / 1.00 и считаем пиксели, которые слой
добавил к плашке (сравнение с P=0, где стоят только плашки).
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
BASE = 'https://piroman99.github.io/zarynka/vn2/index.html'
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

OUT = os.path.join(HERE, '.tmp_vo')
os.makedirs(OUT, exist_ok=True)
S = 1280 / 2400.0
BOX = (620, 330, 1780, 1010)
PROGS = (0.0, 0.05, 0.50, 1.0)


def crop(prog):
    out = os.path.join(OUT, 'live_phr_%s.png' % prog)
    q = ('instant=1&ovlp=%s&auto=0&text=1&voice=0&music=0&node=%d&page=0'
         % (prog, node_index('s3')))
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=9000', '--screenshot=' + out,
                    BASE + '?' + q], capture_output=True, text=True, timeout=170)
    a = np.asarray(Image.open(out).convert('RGB')).astype(np.int16)
    x0, y0, x1, y1 = [int(v * S) for v in BOX]
    return a[y0:y1, x0:x1]


base = crop(0.0)
vals = []
for p in PROGS:
    cur = base if p == 0.0 else crop(p)
    vals.append(int((np.abs(cur - base).sum(axis=2) > 60).sum()))
    print('живое демо, прогресс %.2f: слой добавил %5d px' % (p, vals[-1]))

ok = vals[0] == 0 and vals[1] == 0 and 0 < vals[2] < vals[3]
print('\n%s' % ('OK: на 5 %% надписей нет, на 50 %% часть, на 100 %% всё' if ok
                else 'ПРОБЛЕМА: раскладка по фразам на демо не совпадает'))
sys.exit(0 if ok else 1)
