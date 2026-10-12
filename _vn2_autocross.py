# -*- coding: utf-8 -*-
"""Прогон авто через границу узлов (s1 -> s2 ...) в обычном режиме."""
import os, re, glob, subprocess, html
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]
IDX = 'file://' + os.path.join(HERE, 'vn2', 'index.html')


def dom(q, b):
    p = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--window-size=1280,720',
                        '--virtual-time-budget=%d' % b, '--dump-dom', IDX + '?' + q],
                       capture_output=True, text=True, timeout=120)
    return p.stdout


def state(d):
    t = re.search(r'<div id="text">(.*?)</div>', d, re.S)
    bg = re.search(r'id="bg-a"[^>]*background-image:\s*url\(&quot;([^&]*)&quot;\)', d)
    ch = re.search(r'<div id="chapter">(.*?)</div>', d, re.S)
    e = 'END' if 'class="screen show"' in d and 'id="end"' in d and re.search(r'id="end" class="screen show"', d) else '-'
    return (html.unescape(t.group(1))[:55] if t else '?'), e


q = 'node=2&auto=1&instant=1&text=1&voice=0&music=0'
for b in (1000, 8000, 20000, 40000):
    tx, e = state(dom(q, b))
    print('t=%5ds  %s' % (b // 1000, tx))
