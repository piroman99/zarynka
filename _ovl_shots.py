# -*- coding: utf-8 -*-
"""Скриншоты страниц пролога с титр-слоем (pg.ovl) + лист на глаз."""
import os, sys, glob, subprocess
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

WANT = [('s3', 0), ('s4', 0), ('s5a', 0), ('s5a', 1), ('s5b', 0)]
made = []
for nid, p in WANT:
    ni = node_index(nid)
    q = 'instant=1&auto=0&pause=1&node=%d&page=%d&text=1&voice=0&music=0' % (ni, p)
    out = os.path.join(OUT, 'ovl_%s_%d.png' % (nid, p))
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox',
                        '--disable-dev-shm-usage', '--disable-gpu',
                        '--hide-scrollbars', '--window-size=1280,720',
                        '--virtual-time-budget=6000',
                        '--screenshot=' + out, 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=120)
    ok = os.path.exists(out) and os.path.getsize(out) > 10000
    print(nid, 'page', p, 'node', ni, os.path.getsize(out) if os.path.exists(out) else 'FAIL', r.returncode)
    if ok:
        made.append(('%s · стр.%d' % (nid, p + 1), out))

f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
cw, pad, lab = 1000, 12, 24
ch = int(round(cw * 720 / 1280))
W = cw + 2 * pad
H = sum(ch + lab + pad for _ in made) + pad
cv = Image.new('RGB', (W, H), (14, 16, 22))
d = ImageDraw.Draw(cv)
y = pad
for labt, p in made:
    im = Image.open(p).convert('RGB').resize((cw, ch), Image.LANCZOS)
    cv.paste(im, (pad, y))
    d.rectangle([pad, y, pad + cw - 1, y + ch - 1], outline=(48, 52, 64))
    d.text((pad, y + ch + 2), labt, fill=(214, 218, 226), font=f)
    y += ch + lab + pad
o = os.path.join(HERE, '_sat', 'ovl_shots.png')
cv.save(o)
print('saved', o, cv.size)
