# -*- coding: utf-8 -*-
"""Полный лист приёмной: все 51 страница сеткой (для проверки эмоций/каста)."""
import os, glob, subprocess
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_vo', 'all')
REV = os.path.join(HERE, 'assets', 'review')
os.makedirs(OUT, exist_ok=True)

import json
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
N = len(rec['pages'])

files = []
for p in range(N):
    out = os.path.join(OUT, 'p%02d.png' % p)
    if not os.path.exists(out):
        subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--hide-scrollbars', '--window-size=960,540',
                        '--virtual-time-budget=5000', '--screenshot=' + out,
                        'file://' + IDX + '?instant=1&node=9&page=%d&text=1&voice=0&music=0' % p],
                       capture_output=True, text=True, timeout=120)
    files.append(out)
    if p % 10 == 0:
        print('shot', p)

cw, ch, cols = 384, 216, 9
rows = (N + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * ch), (8, 9, 12))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((cw, ch), Image.LANCZOS)
    x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(im, (x, y))
    pg = rec['pages'][i]
    c = pg.get('cast') or {}
    tag = '%02d %s%s' % (i, (c.get('l') or ['-'])[0][:4],
                         ' / ' + (c.get('r') or ['-'])[0][:4] if c.get('r') else '')
    d.rectangle([x, y, x + 118, y + 13], fill=(0, 0, 0))
    d.text((x + 3, y + 2), tag, fill=(255, 255, 255))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(45, 50, 60))
p = os.path.join(REV, 'review_81_reception_all.png')
sheet.save(p)
print('SHEET', p, sheet.size)
