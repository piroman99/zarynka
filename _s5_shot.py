# -*- coding: utf-8 -*-
"""Скриншот vn2 узла S5 через headless Chromium.

ВАЖНО (баг 2026-10-17): индексы узлов в content.js считаются с титула и значка:
  0 титул, 1 значок, 2=s1, 3=s2, 4=s3, 5=s4, 6=s5, 7=s6, 8=s7, 9 приёмная.
Раньше здесь стоял node=5 -> снимался S4, и лист review_95_s5_vn.png на самом деле
показывал S4 (комната с Марсом на экране). Исправлено на node=6; актуальный скриншот —
assets/review/review_96_s5_vn_ok.png. Универсально: python3 _vn_shot_node.py s1..s7|reception
"""
import os, subprocess, glob
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]
OUT = os.path.join(HERE, 'assets', 'review', 'review_96_s5_vn_ok.png')
NODE = 6  # s5
URL = ('file://' + os.path.join(HERE, 'vn2', 'index.html')
       + '?node=%d&instant=1&text=1&voice=0&music=0' % NODE)
cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
       '--allow-file-access-from-files', '--window-size=1600,900',
       '--virtual-time-budget=2500', '--screenshot=' + OUT, URL]
print('node=%d (s5)' % NODE)
subprocess.run(cmd, check=True)
print('out:', os.path.relpath(OUT, HERE), os.path.getsize(OUT), 'B')
