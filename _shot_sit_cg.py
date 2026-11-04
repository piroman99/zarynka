# -*- coding: utf-8 -*-
"""Скриншоты: сидящий поэт + CG «Муза» в игре. Быстрый лист для Ивана."""
import glob
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]
REV = os.path.join(HERE, 'assets', 'review')
SAT = os.path.join(HERE, '_sat')
ALLEY = node_index('alley')
base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')

GEO = """(() => {const o=[];document.querySelectorAll('#cast .sprite').forEach(s=>{
const op=parseFloat(getComputedStyle(s).opacity); if(op>0.5){const r=s.getBoundingClientRect();
o.push({src:(s.getAttribute('src')||'').split('/').pop(),h:Math.round(r.height),
bottom:Math.round(r.bottom),left:Math.round(r.left)});}});return o;})()"""

SHOTS = [(ALLEY, 0, 'скамейка: он сидит, лица не видно'),
         (ALLEY, 3, 'поднял голову — «Вам плохо?»'),
         (ALLEY, 18, 'CG «Муза» — пиковая страница'),
         (ALLEY, 38, 'Екатерина ушла, он один')]

paths = []
for node, pg, label in SHOTS:
    out = os.path.join(REV, 'review_136_sit_n%d_p%d.png' % (node, pg))
    url = base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0' % (node, pg)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--window-size=1600,900',
                    '--virtual-time-budget=3000', '--screenshot=' + out, url], check=True)
    paths.append((out, label))

b = Browser(1600, 900)
try:
    for node, pg, _l in SHOTS:
        b.navigate(base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0' % (node, pg),
                   wait=1.0)
        print('p%-2d %s' % (pg, json.dumps(b.js(GEO), ensure_ascii=False)))
finally:
    b.close()

tw, th = 800, 450
pad, cap = 10, 26
sheet = Image.new('RGB', (tw * 2 + pad * 3, (th + cap + pad) * 2 + pad), (18, 18, 22))
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
for i, (path, label) in enumerate(paths):
    im = Image.open(path).convert('RGB').resize((tw, th), Image.LANCZOS)
    cx = pad + (i % 2) * (tw + pad)
    cy = pad + (i // 2) * (th + cap + pad)
    sheet.paste(im, (cx, cy))
    d.text((cx + 4, cy + th + 4), label, fill=(235, 225, 205), font=font)
out = os.path.join(SAT, 'sheet_sit_cg.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
