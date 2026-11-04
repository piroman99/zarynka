# -*- coding: utf-8 -*-
"""Пиксельная проверка: титр-слой прирастает СТУПЕНЬКАМИ на фразах страницы.

Прогресс страницы ставится хуком ?ovlp=P (часы озвучки s3 = 16.64 с). Сравниваем кадр
при P с тем же кадром на P=0 (только плашка): считаем пиксели, которые слой ДОБАВИЛ —
так в зачёт идут и кремовые строки, и зелёное «ОБЩЕЕ!» (у него яркость ниже кремовой).
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
IDX = os.path.join(HERE, 'vn2', 'index.html')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index
S = 1280 / 2400.0

BOX = (620, 330, 1780, 1010)      # зона плашки s3 в 2400x1350
PROGS = (0.0, 0.20, 0.50, 0.75, 1.0)


def shot(prog):
    q = ('instant=1&ovlp=%s&auto=0&text=1&voice=0&music=0&node=%d&page=0'
         % (prog, node_index('s3')))
    out = os.path.join(HERE, '.tmp_vo', 'ink_ovl_%s.png' % prog)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=5000', '--screenshot=' + out,
                    'file://' + IDX + '?' + q], capture_output=True, text=True)
    a = np.asarray(Image.open(out).convert('RGB')).astype(np.int16)
    x0, y0, x1, y1 = [int(v * S) for v in BOX]
    return a[y0:y1, x0:x1]


base = shot(0.0)
vals = []
for p in PROGS:
    cur = base if p == 0.0 else shot(p)
    d = np.abs(cur - base).sum(axis=2)
    vals.append(int((d > 60).sum()))
    print('прогресс %.2f: слой добавил %5d px к плашке' % (p, vals[-1]))

bad = 0
if vals[0] != 0:
    print('ПРОБЛЕМА: на 0 %% уже есть надпись (%d)' % vals[0])
    bad += 1
if not (vals[0] < vals[1] < vals[2] < vals[3] <= vals[4]):
    print('ПРОБЛЕМА: прирост не ступеньками: %s' % vals)
    bad += 1

print('\nпроблем: %d' % bad)
sys.exit(1 if bad else 0)
