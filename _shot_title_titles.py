# -*- coding: utf-8 -*-
"""Снимок стартового экрана без титров + с титрами (?titles=1) для сравнения."""
import os
import glob
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
REV = os.path.join(HERE, 'assets', 'review')

for nm, q in (('notitles', 'instant=1&node=0'), ('titles', 'instant=1&node=0&titles=1')):
    out = os.path.join(REV, 'review_117_title_%s.png' % nm)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=5000', '--screenshot=' + out,
                    'file://' + IDX + '?' + q],
                   capture_output=True, text=True, timeout=120)
    print(nm, '->', os.path.basename(out), os.path.getsize(out), 'B')
