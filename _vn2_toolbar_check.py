# -*- coding: utf-8 -*-
"""Проверка DOM-состояния тулбара: auto / paused / off."""
import os, re, glob, subprocess, html
HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]
IDX = 'file://' + os.path.join(VN2, 'index.html')


def dom(q):
    p = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--window-size=1280,720',
                        '--virtual-time-budget=2500', '--dump-dom', IDX + '?' + q],
                       capture_output=True, text=True, timeout=120)
    return p.stdout


def tb(d):
    a = re.search(r'<button id="t-auto"[^>]*class="([^"]*)"', d)
    p = re.search(r'<button id="t-pause"([^>]*)>(.)', d)
    avis = 'hidden' not in (p.group(1) if p else 'hidden')
    return 'auto=[%s] pause_vis=%s pause_lbl=%s' % (a.group(1) if a else '?', avis, p.group(2) if p else '?')


print('OFF   :', tb(dom('node=9&page=0&instant=1')))
print('AUTO  :', tb(dom('node=9&page=0&instant=1&auto=1')))
print('PAUSED:', tb(dom('node=9&page=0&instant=1&auto=1&pause=1')))
