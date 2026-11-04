# -*- coding: utf-8 -*-
"""Локальный снимок кадра 12 (s5b) с титр-слоем: полный кадр + кроп чипа."""
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

ni = node_index('s5b')
URL = ('file://' + IDX + '?instant=1&auto=0&pause=1&pace=0&node=%d&page=0'
       '&text=1&voice=0&music=0' % ni)
p = os.path.join(OUT, 's5b_A.png')
subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                '--virtual-time-budget=10000', '--screenshot=' + p, URL],
               capture_output=True, text=True, timeout=180)
im = Image.open(p).convert('RGB')
W, H = im.size
print('full', im.size, 'node', ni)
k = W / 2400.0
box = (int(600 * k), int(640 * k), int(1800 * k), int(830 * k))
c = im.crop(box)
c = c.resize((c.size[0] * 2, c.size[1] * 2), Image.LANCZOS)
sheet = Image.new('RGB', (max(c.size[0], 1152) + 24, c.size[1] + 648 + 60), (14, 16, 22))
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
sheet.paste(im.resize((1152, 648), Image.LANCZOS), (12, 12))
sheet.paste(c, (12, 12 + 648 + 30))
d = ImageDraw.Draw(sheet)
d.text((12, 648 + 16), 's5b вариант A: центр 1200, y 735', fill=(214, 218, 226), font=f)
o = os.path.join(OUT, 's5b_A.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
