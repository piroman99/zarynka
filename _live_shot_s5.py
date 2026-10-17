# -*- coding: utf-8 -*-
"""Живая проверка: снимаем ОНЛАЙН-версию узла S5 (GitHub Pages) headless-хромом."""
import os, subprocess, glob
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]
OUT = os.path.join(HERE, 'assets', 'review', 'review_98_s5_live_pages.png')
URL = 'https://piroman99.github.io/zarynka/vn2/?node=6&instant=1&text=1&voice=0&music=0'
cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
       '--window-size=1600,900', '--virtual-time-budget=9000',
       '--screenshot=' + OUT, URL]
subprocess.run(cmd, check=True)
print('live ->', os.path.relpath(OUT, HERE), os.path.getsize(OUT), 'B')
