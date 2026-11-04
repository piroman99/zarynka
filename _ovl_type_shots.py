# -*- coding: utf-8 -*-
"""Снимки стадий набора надписи в кадре (вариант B, 2026-11-04).

Хук `?ovln=N` (instant=1 + ровно N букв): под виртуальным временем Chrome CSS-анимация
замирает на кадре opacity:0, поэтому живой набор снимком не поймать — показываем стадии.
Рядом с каждым кадром — счёт «чернильных» пикселей внутри плашки (растёт с числом букв).
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_vo')
os.makedirs(OUT, exist_ok=True)
S = 1280 / 2400.0

# (узел, страница, сколько букв, зона плашки 2400x1350, порог яркости, подпись)
SHOTS = [('s3', 0, 0, (620, 330, 1780, 1010), 600, 's3 · 0 букв — только плашка'),
         ('s3', 0, 13, (620, 330, 1780, 1010), 600, 's3 · 13 букв — набор идёт'),
         ('s3', 0, 47, (620, 330, 1780, 1010), 600, 's3 · 47 букв — набор закончен'),
         ('s5b', 0, 9, (801, 690, 1599, 780), 450, 's5b · 9 букв — чип набирается'),
         ('s5b', 0, 20, (801, 690, 1599, 780), 450, 's5b · 20 букв — чип целиком')]

made = []
for nid, p, n, box, thr, label in SHOTS:
    q = ('instant=1&ovln=%d&auto=0&text=1&voice=0&music=0&node=%d&page=%d'
         % (n, node_index(nid), p))
    out = os.path.join(OUT, 'type_%s_%d_%d.png' % (nid, p, n))
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox',
                        '--disable-dev-shm-usage', '--disable-gpu',
                        '--hide-scrollbars', '--window-size=1280,720',
                        '--virtual-time-budget=6000',
                        '--screenshot=' + out, 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=180)
    if not (os.path.exists(out) and os.path.getsize(out) > 10000):
        print('FAIL', nid, n, r.returncode)
        continue
    a = np.asarray(Image.open(out).convert('RGB')).astype(np.int16)
    x0, y0, x1, y1 = [int(v * S) for v in box]
    lum = a[y0:y1, x0:x1].sum(axis=2)
    px = int((lum > thr).sum())
    print('%-4s %2d букв: %5d чернильных px  (%s)' % (nid, n, px, label))
    made.append(('%s — %d px краски' % (label, px), out))

f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
cw, pad, lab = 1000, 12, 24
ch = int(round(cw * 720 / 1280))
W = cw + 2 * pad
H = sum(ch + lab + pad for _ in made) + pad
cv = Image.new('RGB', (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
y = pad
for labt, pth in made:
    im = Image.open(pth).convert('RGB').resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 2), labt, fill=(214, 218, 226), font=f)
    y += ch + lab + pad
o = os.path.join(HERE, '_sat', 'ovl_type.png')
cv.save(o)
print('saved', o, cv.size)
