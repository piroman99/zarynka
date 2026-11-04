# -*- coding: utf-8 -*-
"""Скриншоты приёмной на входе Екатерины (стр. 2-4) + лист для Ивана."""
import glob
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _vn2_nodes import node_index  # noqa: E402

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]
REC = node_index('reception')
OUT = os.path.join(HERE, 'assets', 'review')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)
base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')

pages = [(2, 'до: пауза, поэта отправили восвояси'),
         (3, 'ОПИСАНИЕ: «кудрявые седые…» — она входит'),
         (4, 'приветствие «Добрый день»')]
shots = []
for pg, label in pages:
    out = os.path.join(OUT, 'review_133_kate_enter_p%d.png' % pg)
    url = base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0' % (REC, pg)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--window-size=1600,900',
                    '--virtual-time-budget=3000', '--screenshot=' + out, url], check=True)
    print('shot page', pg, '->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
    shots.append((out, label))

# лист: три кадра вертикально, с подписями
W, H = 1600, 900
scale = 0.5
tw, th = int(W * scale), int(H * scale)
pad, cap = 10, 26
sheet = Image.new('RGB', (tw + pad * 2, (th + cap + pad) * len(shots) + pad), (18, 18, 22))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
except Exception:
    font = ImageFont.load_default()
y = pad
for path, label in shots:
    im = Image.open(path).convert('RGB').resize((tw, th), Image.LANCZOS)
    sheet.paste(im, (pad, y))
    d.text((pad + 4, y + th + 4), label, fill=(235, 225, 205), font=font)
    y += th + cap + pad
out = os.path.join(SAT, 'sheet_kate_enter.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
