# -*- coding: utf-8 -*-
"""Снимок титула: круглое лого с прозрачным фоном не должно дать белого ореола."""
import os
import glob
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
out = os.path.join(HERE, 'assets', 'review', 'review_116_title_round.png')
subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                '--virtual-time-budget=5000', '--screenshot=' + out,
                'file://' + os.path.join(HERE, 'vn2', 'index.html') + '?instant=1&node=0'],
               capture_output=True, text=True, timeout=120)
print('->', out, os.path.getsize(out), 'B')
