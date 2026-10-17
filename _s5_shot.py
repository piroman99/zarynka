# -*- coding: utf-8 -*-
"""Скриншот vn2 узла S5 (node=5) через headless Chromium — визуальная сверка финала."""
import os, subprocess, glob
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]
OUT = os.path.join(HERE, 'assets', 'review', 'review_95_s5_vn.png')
URL = 'file://' + os.path.join(HERE, 'vn2', 'index.html') + '?node=5&instant=1&text=1&voice=0&music=0'
cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
       '--allow-file-access-from-files', '--window-size=1600,900',
       '--virtual-time-budget=2500', '--screenshot=' + OUT, URL]
print('chrome:', CHROME)
subprocess.run(cmd, check=True)
print('out:', os.path.relpath(OUT, HERE), os.path.getsize(OUT), 'B')
