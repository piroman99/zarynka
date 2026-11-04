# -*- coding: utf-8 -*-
"""Скриншоты приёмной: поэт в кадре (стр. 0) и уход (стр. 1) + лист Ивану.

Меряет в движке геометрию спрайтов (#cast .sprite): высота, низ, левая граница —
чтобы видеть, одного ли роста поэт и Сергей.
"""
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
REC = node_index('reception')
OUT = os.path.join(HERE, 'assets', 'review')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)
base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')

GEO = """(() => {
  const out = [];
  document.querySelectorAll('#cast .sprite').forEach(s => {
    const r = s.getBoundingClientRect();
    out.push({src: s.getAttribute('src'), slot: s.dataset.slot,
              h: Math.round(r.height), bottom: Math.round(r.bottom),
              left: Math.round(r.left), w: Math.round(r.width)});
  });
  return out;
})()"""

pages = [(0, 'поэт в кадре: «двое студентов и модель… поэт»'),
         (1, 'поэт ушёл: «отправил вслед за остальными»')]
shots = []
for pg, label in pages:
    url = base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0' % (REC, pg)
    out = os.path.join(OUT, 'review_134_poet_p%d.png' % pg)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--window-size=1600,900',
                    '--virtual-time-budget=3000', '--screenshot=' + out, url], check=True)
    shots.append((out, label))
    print('shot', pg, os.path.relpath(out, HERE))

b = Browser(1600, 900)
try:
    for pg, _l in pages:
        b.navigate(base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0' % (REC, pg),
                   wait=1.2)
        g = b.js(GEO)
        print('page %d: %s' % (pg, json.dumps(g, ensure_ascii=False)))
finally:
    b.close()

pad, cap = 10, 26
scale = 0.5
tw, th = int(1600 * scale), int(900 * scale)
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
out = os.path.join(SAT, 'sheet_poet_in_vn.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
