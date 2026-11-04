# -*- coding: utf-8 -*-
"""Что под плашкой и вокруг неё: нативный кроп панели кадра 11 в живом демо,
и тот же кроп без титр-слоя (?ovl=0) — ищем, не наехали ли буквы на нарисованное."""
import os
import glob
import subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
BASE = ('https://piroman99.github.io/zarynka/vn2/index.html'
        '?instant=1&auto=0&pause=1&pace=0&node=9&page=0&text=1&voice=0&music=0')
OUT = os.path.join(HERE, '_sat')

shots = []
for tag, extra in (('with_ovl', ''), ('no_ovl', '&ovl=0')):
    p = os.path.join(OUT, 'demo_s5a_%s.png' % tag)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=12000', '--screenshot=' + p, BASE + extra],
                   capture_output=True, text=True, timeout=180)
    im = Image.open(p).convert('RGB')
    W, H = im.size
    k = W / 2400.0
    box = (int(1050 * k), int(440 * k), int(1920 * k), int(950 * k))
    c = im.crop(box)
    c = c.resize((c.size[0] * 2, c.size[1] * 2), Image.LANCZOS)
    shots.append((tag, c))
    print(tag, im.size, 'crop', c.size)

pad, lab = 12, 24
cw = max(c.size[0] for _, c in shots)
ch = max(c.size[1] for _, c in shots)
sheet = Image.new('RGB', (cw + 2 * pad, len(shots) * (ch + lab + pad) + pad), (14, 16, 22))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
y = pad
for t, c in shots:
    sheet.paste(c, (pad, y))
    d.text((pad, y + ch + 2), t, fill=(214, 218, 226), font=f)
    y += ch + lab + pad
o = os.path.join(OUT, 's5a_zoom.png')
sheet.save(o)
print('saved', os.path.relpath(o, HERE), sheet.size)
