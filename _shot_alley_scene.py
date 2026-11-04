# -*- coding: utf-8 -*-
"""Скриншоты новой сцены «аллея у ворот» + лист Ивану.

Снимает: ступени (обе страницы), скамейку (первая страница), момент «Вам плохо?»,
визитку и последнюю страницу (Екатерина ушла — поэт один по центру).
Печатает геометрию спрайтов из движка.
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
REV = os.path.join(HERE, 'assets', 'review')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)
base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
STEPS = node_index('steps')
ALLEY = node_index('alley')

GEO = """(() => {
  const out = [];
  document.querySelectorAll('#cast .sprite').forEach(s => {
    const op = parseFloat(getComputedStyle(s).opacity);
    if (op > 0.5) {
      const r = s.getBoundingClientRect();
      out.push({src: (s.getAttribute('src')||'').split('/').pop(), slot: s.dataset.slot,
                h: Math.round(r.height), bottom: Math.round(r.bottom), left: Math.round(r.left)});
    }
  });
  return out;
})()"""

SHOTS = [
    (STEPS, 0, 'ступени: «вышла из дверей приёмной»'),
    (STEPS, 1, 'ступени: «повернула на аллею»'),
    (ALLEY, 0, 'аллея: «на скамейке… сидел юноша»'),
    (ALLEY, 3, '«Вам плохо?» — он поднял лицо'),
    (ALLEY, 21, '«Держите» — визитка, он заинтересовался'),
    (ALLEY, 38, 'Екатерина ушла, поэт один'),
]

paths = []
for node, pg, label in SHOTS:
    out = os.path.join(REV, 'review_135_alley_n%d_p%d.png' % (node, pg))
    url = base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0' % (node, pg)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--window-size=1600,900',
                    '--virtual-time-budget=3000', '--screenshot=' + out, url], check=True)
    paths.append((out, label))
    print('shot', node, pg, os.path.relpath(out, HERE))

b = Browser(1600, 900)
try:
    for node, pg, _l in SHOTS:
        b.navigate(base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0' % (node, pg),
                   wait=1.2)
        print('n%d p%-2d %s' % (node, pg, json.dumps(b.js(GEO), ensure_ascii=False)))
finally:
    b.close()

# лист 2x3
tw, th = 800, 450
pad, cap = 10, 26
cols, rows = 2, 3
sheet = Image.new('RGB', (tw * cols + pad * (cols + 1), (th + cap + pad) * rows + pad), (18, 18, 22))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
except Exception:
    font = ImageFont.load_default()
for i, (path, label) in enumerate(paths):
    im = Image.open(path).convert('RGB').resize((tw, th), Image.LANCZOS)
    cx = pad + (i % cols) * (tw + pad)
    cy = pad + (i // cols) * (th + cap + pad)
    sheet.paste(im, (cx, cy))
    d.text((cx + 4, cy + th + 4), label, fill=(235, 225, 205), font=font)
out = os.path.join(SAT, 'sheet_alley_scene.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
