# -*- coding: utf-8 -*-
"""Точечные скриншоты vn2: python3 _vn2_shot_pages.py 0 1 2 45"""
import os, sys, glob, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_vo')
os.makedirs(OUT, exist_ok=True)

pages = sys.argv[1:] or ['0', '1', '2']
for p in pages:
    q = 'instant=1&node=9&page=%s&text=1&voice=0&music=0' % p
    out = os.path.join(OUT, 'shot_p%s.png' % p)
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox',
                        '--disable-dev-shm-usage', '--disable-gpu',
                        '--hide-scrollbars', '--window-size=1280,720',
                        '--virtual-time-budget=6000',
                        '--screenshot=' + out, 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=120)
    print(p, os.path.getsize(out) if os.path.exists(out) else 'FAIL', r.returncode)
