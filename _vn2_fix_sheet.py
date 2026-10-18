# -*- coding: utf-8 -*-
"""Контактный лист кадров приёмной после правок: каст, эмоции, Старик."""
import os, glob, subprocess
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_vo')
os.makedirs(OUT, exist_ok=True)

SHOTS = [(0, 'p00 Старик (флешбэк)'), (1, 'p01 Старик говорит'),
         (2, 'p02 Старик'), (3, 'p03 Сергей один'),
         (6, 'p06 входит Катя'), (18, 'p18 Сергей concerned'),
         (32, 'p32 Катя sad'), (49, 'p49 Сергей smile'),
         (50, 'p50 Катя smile')]

files = []
for p, label in SHOTS:
    out = os.path.join(OUT, 'fix_p%02d.png' % p)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=6000', '--screenshot=' + out,
                    'file://' + IDX + '?instant=1&node=9&page=%d&text=1&voice=0&music=0' % p],
                   capture_output=True, text=True, timeout=120)
    files.append((out, label))
    print(p, label, 'ok')

cw, ch, cols = 640, 360, 3
rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw, rows * ch), (10, 12, 18))
d = ImageDraw.Draw(sheet)
for i, (f, label) in enumerate(files):
    im = Image.open(f).convert('RGB').resize((cw, ch), Image.LANCZOS)
    x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(40, 44, 56))
    d.rectangle([x, y, x + 190, y + 18], fill=(0, 0, 0))
    d.text((x + 6, y + 4), label, fill=(255, 255, 255))
p = os.path.join(HERE, 'assets', 'review', 'review_71_vn2_cast_fix.png')
sheet.save(p)
print('SHEET', p, sheet.size)
