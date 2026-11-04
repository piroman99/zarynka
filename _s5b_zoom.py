# -*- coding: utf-8 -*-
"""Кадр 12 (s5b, «Волна требований докатилась до Верховного Совета»): живое демо,
полный кадр + нативный кроп чипа. Ищем, куда уехали буквы."""
import os
import glob
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
OUT = os.path.join(HERE, '_sat')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

ni = node_index('s5b')
print('node s5b =', ni)
URL = ('https://piroman99.github.io/zarynka/vn2/index.html'
       '?instant=1&auto=0&pause=1&pace=0&node=%d&page=0&text=1&voice=0&music=0' % ni)
p = os.path.join(OUT, 'demo_s5b.png')
subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                '--virtual-time-budget=12000', '--screenshot=' + p, URL],
               capture_output=True, text=True, timeout=180)
im = Image.open(p).convert('RGB')
W, H = im.size
print('full', im.size)

k = W / 2400.0
crops = [('чип + окрестности', (int(400 * k), int(700 * k), int(1700 * k), int(1050 * k)))]
parts = []
for t, box in crops:
    c = im.crop(box)
    c = c.resize((c.size[0] * 2, c.size[1] * 2), Image.LANCZOS)
    parts.append((t, c))
parts.insert(0, ('кадр целиком', im.resize((1152, 648), Image.LANCZOS)))

pad, lab = 12, 24
cw = max(c.size[0] for _, c in parts)
sheet_h = sum(c.size[1] + lab + pad for _, c in parts) + pad
sheet = Image.new('RGB', (cw + 2 * pad, sheet_h), (14, 16, 22))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
y = pad
for t, c in parts:
    sheet.paste(c, (pad, y))
    d.text((pad, y + c.size[1] + 2), t, fill=(214, 218, 226), font=f)
    y += c.size[1] + lab + pad
o = os.path.join(OUT, 's5b_zoom.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
