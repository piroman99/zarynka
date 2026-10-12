# -*- coding: utf-8 -*-
"""Лист для оценки: спрайты, эмоции, диссолв, два персонажа. -> review_76_vn2_sprites.png"""
import os, subprocess, glob
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]
REV = os.path.join(HERE, 'assets', 'review')
IDX = os.path.join(HERE, 'vn2', 'index.html')
TMP = os.path.join(HERE, '_tmp_sprite_review')
os.makedirs(TMP, exist_ok=True)

# (имя, query, virtual-time-budget ms)
TILES = [
    ('1_sergey_smile', 'node=9&page=8&text=1&voice=0&music=0', 5000),
    ('2_both',         'node=9&page=10&text=1&voice=0&music=0', 5000),
    ('3_sergey_sad',   'node=9&page=24&text=1&voice=0&music=0', 5000),
    ('4_kate_sad',     'node=9&page=32&text=1&voice=0&music=0', 5000),
    ('5_dissolve',     'node=9&page=10&text=1&voice=0&music=0', 240),
    ('6_narration',    'node=9&page=45&text=1&voice=0&music=0', 5000),
]

# для «чистой» картинки (без текста набора) — instant только там, где нужен готовый текст
files = []
for nm, q, budget in TILES:
    inst = '&instant=1' if nm != '5_dissolve' else ''
    url = 'file://' + IDX + '?voice=0&music=0' + inst + '&' + q
    out = os.path.join(TMP, nm + '.png')
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=%d' % budget, '--screenshot=' + out, url],
                   capture_output=True, text=True, timeout=90)
    files.append((nm, out))
    print(nm, 'ok')

cols, rows, cw, ch = 3, 2, 640, 360
sheet = Image.new('RGB', (cols * cw, rows * ch + 0), (10, 12, 18))
d = ImageDraw.Draw(sheet)
font = None
for fp in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if os.path.exists(fp):
        font = ImageFont.truetype(fp, 20); break
for i, (nm, f) in enumerate(files):
    im = Image.open(f).convert('RGB').resize((cw, ch), Image.LANCZOS)
    x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + cw - 1, y + ch - 1], outline=(40, 44, 56))
    d.rectangle([x, y, x + 250, y + 30], fill=(10, 12, 18))
    d.text((x + 10, y + 5), nm, fill=(240, 210, 120), font=font)
out = os.path.join(REV, 'review_76_vn2_sprites.png')
sheet.save(out)
print('WROTE', out, sheet.size)
