# -*- coding: utf-8 -*-
"""Живое демо (piroman99.github.io): буквы надписи набираются по фразе.

Грузим опубликованную сборку, `?ovln=N` показывает ровно N букв — по снимкам видно, что
строка растёт. Меряем «чернильные» пиксели внутри плашки (s3 — кремовая строка, порог 600;
s5b — золотой чип, порог 450).
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

CASES = [('s3', 0, (620, 330, 1780, 1010), 600, (0, 13, 47)),
         ('s5b', 0, (801, 690, 1599, 780), 450, (0, 9, 20))]

bad = 0
for nid, p, box, thr, ns in CASES:
    vals = []
    for n in ns:
        q = ('instant=1&ovln=%d&auto=0&text=1&voice=0&music=0&node=%d&page=%d'
             % (n, node_index(nid), p))
        out = os.path.join(OUT, 'live_type_%s_%d.png' % (nid, n))
        subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                        '--virtual-time-budget=9000', '--screenshot=' + out,
                        BASE + '?' + q], capture_output=True, text=True, timeout=180)
        if not os.path.exists(out):
            print('%s ovln=%d: снимок не получен' % (nid, n))
            bad += 1
            break
        a = np.asarray(Image.open(out).convert('RGB')).astype(np.int16)
        x0, y0, x1, y1 = [int(v * S) for v in box]
        vals.append(int((a[y0:y1, x0:x1].sum(axis=2) > thr).sum()))
    ok = len(vals) == len(ns) and vals[0] < vals[1] < vals[-1]
    print('%s: буквы %s → краски %s px  %s'
          % (nid, list(ns), vals, 'OK' if ok else 'ПРОБЛЕМА: не растёт'))
    if not ok:
        bad += 1

print('\nпроблем: %d' % bad)
sys.exit(1 if bad else 0)
