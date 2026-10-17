# -*- coding: utf-8 -*-
"""Снимки узлов простым headless-хромом (--screenshot): S5 и Приёмная, после перехода на WebP."""
import os, subprocess, glob, shutil
from PIL import Image, ImageChops
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]
REV = os.path.join(HERE, 'assets', 'review')

ref = os.path.join(REV, 'review_96_s5_vn_ok.png')
ref_copy = os.path.join(REV, '_ref_s5_png.png')
if os.path.exists(ref) and not os.path.exists(ref_copy):
    shutil.copy2(ref, ref_copy)
    print('эталон PNG-версии сохранён ->', os.path.basename(ref_copy))

JOBS = [('s5', 6, 'review_96_s5_vn_ok.png'), ('reception', 9, 'review_101_reception_webp.png')]
for name, node, out in JOBS:
    url = ('file://' + os.path.join(HERE, 'vn2', 'index.html')
           + '?node=%d&instant=1&text=1&voice=0&music=0' % node)
    p = os.path.join(REV, out)
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--window-size=1600,900',
                    '--virtual-time-budget=3000', '--screenshot=' + p, url],
                   capture_output=True, timeout=180)
    print('%-10s node=%d -> %-24s %d B' % (name, node, out, os.path.getsize(p)))

if os.path.exists(ref_copy):
    a = Image.open(ref_copy).convert('RGB')
    c = Image.open(os.path.join(REV, 'review_96_s5_vn_ok.png')).convert('RGB')
    if a.size != c.size:
        c = c.resize(a.size)
    d = np.asarray(ImageChops.difference(a, c), np.float32)
    print('S5 рендер PNG vs WebP: MAE %.3f / 255, макс %d -> %s'
          % (d.mean(), d.max(), 'идентично' if d.mean() < 1.5 else 'ЕСТЬ РАЗЛИЧИЯ'))
