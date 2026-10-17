# -*- coding: utf-8 -*-
"""Скриншот vn2 узла S5 через headless Chromium.
ВАЖНО: индексы узлов в content.js: 0 титул, 1 значок, 2=s1, 3=s2, 4=s3, 5=s4, 6=s5, 7=s6, 8=s7, 9 приёмная.
Раньше здесь стоял node=5 -> снимался S4. Исправлено на 6.
"""
import os, subprocess, glob, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]

NODE = {'s1': 2, 's2': 3, 's3': 4, 's4': 5, 's5': 6, 's6': 7, 's7': 8, 'reception': 9}
which = sys.argv[1] if len(sys.argv) > 1 else 's5'
node = NODE[which]
OUT = os.path.join(HERE, 'assets', 'review', 'review_96_%s_vn_ok.png' % which)
URL = ('file://' + os.path.join(HERE, 'vn2', 'index.html')
       + '?node=%d&instant=1&text=1&voice=0&music=0' % node)
cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
       '--allow-file-access-from-files', '--window-size=1600,900',
       '--virtual-time-budget=2500', '--screenshot=' + OUT, URL]
print('node=%d (%s)' % (node, which))
subprocess.run(cmd, check=True)
print('out:', os.path.relpath(OUT, HERE), os.path.getsize(OUT), 'B')
