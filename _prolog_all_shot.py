# -*- coding: utf-8 -*-
"""Все кадры пролога локально: сетка 2 колонки, чтобы глазами проверить надписи
и метки сцен на каждом. Плюс отдельный лист кропов титр-слоя."""
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
IDX = os.path.join(HERE, 'vn2', 'index.html')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

SHOTS = [('s1', 0), ('p6', 0), ('p7', 0), ('p8', 0), ('s3', 0), ('s4', 0),
         ('s5a', 0), ('s5a', 1), ('s5b', 0), ('s6', 0), ('s7', 0)]
tmp = os.path.join(OUT, '_all')
os.makedirs(tmp, exist_ok=True)
tiles = []
for name, page in SHOTS:
    ni = node_index(name)
    url = ('file://' + IDX + '?instant=1&auto=0&pause=1&pace=0&node=%d&page=%d'
           '&text=1&voice=0&music=0' % (ni, page))
    p = os.path.join(tmp, '%s_%d.png' % (name, page))
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=9000', '--screenshot=' + p, url],
                   capture_output=True, text=True, timeout=180)
    tiles.append(('%s / стр.%d' % (name, page), Image.open(p).convert('RGB')))
    print('shot', name, page)

cw, ch = 620, 349
pad, lab = 10, 22
rows = (len(tiles) + 1) // 2
sheet = Image.new('RGB', (2 * (cw + pad) + pad, rows * (ch + lab + pad) + pad), (14, 16, 22))
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(tiles):
    cx, cy = pad + (i % 2) * (cw + pad), pad + (i // 2) * (ch + lab + pad)
    sheet.paste(im.resize((cw, ch), Image.LANCZOS), (cx, cy))
    d.text((cx, cy + ch + 3), t, fill=(214, 218, 226), font=f)
o = os.path.join(OUT, 'prolog_all.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
