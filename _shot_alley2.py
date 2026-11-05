# -*- coding: utf-8 -*-
"""Лист проверки сцены «аллея» после правки: сидящий поэт + проп-скамейка.

Снимает три варианта посадки (скамейка A/B/C по высоте) и лист эмоций,
чтобы Иван одной буквой выбрал высоту скамейки, а я записал число — 0 ₽.
"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

REV = os.path.join(HERE, 'assets', 'review')
SAT = os.path.join(HERE, '_sat')
os.makedirs(REV, exist_ok=True)
os.makedirs(SAT, exist_ok=True)
ALLEY = node_index('alley')
base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')

GEO = """(() => {
 const o = {prop: null, cast: []};
 const p = document.querySelector('#props .prop');
 if (p && getComputedStyle(p).opacity > .5) { const r = p.getBoundingClientRect();
   o.prop = {src: (p.getAttribute('src')||'').split('/').pop(), h: Math.round(r.height),
             top: Math.round(r.top), bottom: Math.round(r.bottom),
             left: Math.round(r.left), right: Math.round(r.right)}; }
 document.querySelectorAll('#cast .sprite').forEach(s => {
   const op = parseFloat(getComputedStyle(s).opacity);
   if (op > .5) { const r = s.getBoundingClientRect();
     o.cast.push({src: (s.getAttribute('src')||'').split('/').pop(), h: Math.round(r.height),
                  top: Math.round(r.top), bottom: Math.round(r.bottom),
                  left: Math.round(r.left), right: Math.round(r.right),
                  seated: s.classList.contains('seated')}); } });
 return o; })()"""

# (узел, страница, подпись, сдвиг низа пропа)
SHOTS = [
    (ALLEY, 0, 'A · скамейка -6% (базовая посадка)', None),
    (ALLEY, 0, 'B · скамейка -3% (выше на 27 px)', '-3%'),
    (ALLEY, 0, 'C · скамейка -9% (ниже на 27 px)', '-9%'),
    (ALLEY, 3, 'он поднял голову (neutral)', None),
    (ALLEY, 21, 'после CG: покраснел, отвернулся (shy)', None),
    (ALLEY, 38, 'Екатерина ушла — он один', None),
]

paths = []
b = Browser(1600, 900)
try:
    for node, pg, label, bottom in SHOTS:
        url = base + '?node=%d&page=%d&instant=1&text=1&voice=0&music=0&auto=0' % (node, pg)
        b.navigate(url, wait=0.9)
        if bottom:
            b.js("(() => {const p=document.querySelector('#props .prop'); p.style.bottom='%s'; return 1;})()"
                 % bottom)
        out = os.path.join(REV, 'alley2_n%d_p%d%s.png' % (node, pg, '_' + bottom.strip('-').replace('%', '') if bottom else ''))
        b.shot(out)
        geo = b.js(GEO)
        print('p%-2d %-38s %s' % (pg, label, json.dumps(geo, ensure_ascii=False)))
        paths.append((out, label))
finally:
    b.close()

tw, th = 800, 450
pad, cap = 8, 24
cols, rows = 2, (len(paths) + 1) // 2
sheet = Image.new('RGB', (tw * cols + pad * (cols + 1), (th + cap + pad) * rows + pad), (18, 18, 22))
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 17)
for i, (p, label) in enumerate(paths):
    im = Image.open(p).convert('RGB').resize((tw, th), Image.LANCZOS)
    cx = pad + (i % cols) * (tw + pad)
    cy = pad + (i // cols) * (th + cap + pad)
    sheet.paste(im, (cx, cy))
    d.text((cx + 4, cy + th + 3), label, fill=(235, 225, 205), font=font)
out = os.path.join(SAT, 'sheet_alley2.png')
sheet.save(out)
print('sheet ->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
