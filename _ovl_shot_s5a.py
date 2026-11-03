# -*- coding: utf-8 -*-
"""Скриншоты кадра 11 (s5a) с титр-слоем + точный диф-бокс слоя (снимок с ?ovl=0).
Лист на глаз: _sat/s5a_final.png."""
import os
import glob
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_vo')
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

TARGET = (1119, 505, 1848, 890)


def shot(q, out):
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=6000', '--screenshot=' + out,
                    'file://' + IDX + '?' + q], capture_output=True, text=True, timeout=180)
    return out


def diffbox(a, b):
    A, B = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
    W, H = A.size
    pa, pb = A.load(), B.load()
    xs, ys = [], []
    for y in range(H):
        for x in range(W):
            ra, ga, ba = pa[x, y]
            rb, gb, bb = pb[x, y]
            if abs(ra - rb) + abs(ga - gb) + abs(ba - bb) > 24:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    k = 2400.0 / W
    return (int(min(xs) * k), int(min(ys) * k), int(max(xs) * k), int(max(ys) * k))


made = []
for p in (0, 1):
    base = ('instant=1&auto=0&pause=1&pace=0&node=%d&page=%d&text=1&voice=0&music=0'
            % (node_index('s5a'), p))
    on = shot(base, os.path.join(OUT, 's5a_final_%d.png' % p))
    off = shot(base + '&ovl=0', os.path.join(OUT, 's5a_final_%d_off.png' % p))
    bb = diffbox(on, off)
    ok = bb and all(abs(bb[i] - TARGET[i]) <= 6 for i in range(4))
    print('page %d  layer bbox2400=%s  target=%s  %s'
          % (p, bb, TARGET, 'OK' if ok else 'MISMATCH'))
    made.append(('s5a · стр.%d  слой %s  %s' % (p + 1, bb, 'OK' if ok else 'MISMATCH'), on))

cw, pad, lab = 1120, 12, 26
ch = int(round(cw * 720 / 1280))
sheet = Image.new('RGB', (cw + 2 * pad, len(made) * (ch + lab + pad) + pad), (14, 16, 22))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
y = pad
for t, p in made:
    sheet.paste(Image.open(p).convert('RGB').resize((cw, ch), Image.LANCZOS), (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 4), t, fill=(214, 218, 226), font=f)
    y += ch + lab + pad
o = os.path.join(HERE, '_sat', 's5a_final.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
