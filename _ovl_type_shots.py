# -*- coding: utf-8 -*-
"""Снимки кадра s3 на трёх фразах: строка приходит со своей фразой (не все сразу).

?ovlp=P ставит прогресс страницы (по озвучке 16.64 с): P=0.20 — прозвучало «Марс — дело
общее?», P=0.50 — добавлен хор «Общее!», P=0.75 — добавлен «а что же обычных людей нет?».
Плюс s4 на 0.80 (подпись на экране панели) и чип s5b на 0.85.
"""
import glob
import os
import subprocess
import sys

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

SHOTS = [('s3', 0, 0.20, 's3 · 20 % — «Марс — дело общее?»'),
         ('s3', 0, 0.50, 's3 · 50 % — хор: «Общее!»'),
         ('s3', 0, 0.75, 's3 · 75 % — «а что же обычных людей нет?»'),
         ('s4', 0, 0.80, 's4 · 80 % — подпись на экране панели'),
         ('s5b', 0, 0.85, 's5b · 85 % — чип «два места»')]

made = []
for nid, p, prog, label in SHOTS:
    q = ('instant=1&ovlp=%s&auto=0&text=1&voice=0&music=0&node=%d&page=%d'
         % (prog, node_index(nid), p))
    out = os.path.join(OUT, 'phrase_%s_%s.png' % (nid, prog))
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox',
                        '--disable-dev-shm-usage', '--disable-gpu',
                        '--hide-scrollbars', '--window-size=1280,720',
                        '--virtual-time-budget=5000',
                        '--screenshot=' + out, 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=180)
    if not (os.path.exists(out) and os.path.getsize(out) > 10000):
        print('FAIL', nid, prog, r.returncode)
        continue
    print('%-4s %.2f  %d B  %s' % (nid, prog, os.path.getsize(out), label))
    made.append((label, out))

f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
cw, pad, lab = 1000, 12, 24
ch = int(round(cw * 720 / 1280))
W = cw + 2 * pad
Hh = sum(ch + lab + pad for _ in made) + pad
cv = Image.new('RGB', (W, Hh), (14, 16, 22))
d = ImageDraw.Draw(cv)
y = pad
for labt, pth in made:
    im = Image.open(pth).convert('RGB').resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 2), labt, fill=(214, 218, 226), font=f)
    y += ch + lab + pad
o = os.path.join(HERE, '_sat', 'ovl_phrases.png')
cv.save(o)
print('saved', o, cv.size)
