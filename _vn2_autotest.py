# -*- coding: utf-8 -*-
"""Диагностика авто-режима vn2 через chromium --dump-dom + виртуальное время."""
import os, re, glob, subprocess, html
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]
IDX = 'file://' + os.path.join(HERE, 'vn2', 'index.html')


def dom(q, budget=12000):
    p = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--window-size=1280,720',
                        '--virtual-time-budget=%d' % budget, '--dump-dom', IDX + '?' + q],
                       capture_output=True, text=True, timeout=120)
    return p.stdout


def text_of(d):
    m = re.search(r'<div id="text">(.*?)</div>', d, re.S)
    return html.unescape(m.group(1))[:90] if m else '(нет #text)'


for q in ['node=9&page=0&auto=1&instant=1&text=1&voice=0&music=0',
          'node=9&page=0&auto=0&instant=1&text=1&voice=0&music=0']:
    print('Q:', q)
    print('  t=3s  :', text_of(dom(q, 3000)))
    print('  t=12s :', text_of(dom(q, 12000)))
