# -*- coding: utf-8 -*-
"""Дамп DOM для s4 (node 8) и s5b (node 10): какие inline-стили у элементов слоя."""
import os, sys, glob, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

for nid, p in (('s3', 0), ('s4', 0), ('s5b', 0)):
    q = ('instant=1&auto=0&pause=1&pace=0&node=%d&page=%d&text=1&voice=0&music=0'
         % (node_index(nid), p))
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
                        '--disable-dev-shm-usage', '--hide-scrollbars',
                        '--window-size=1280,720', '--virtual-time-budget=6000',
                        '--dump-dom', 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=180)
    m = re.search(r'<div id="ovl".*?</div>', r.stdout, re.S)
    o = re.sub(r'\s+', ' ', m.group(0)) if m else '(нет #ovl)'
    print('===', nid, 'node', node_index(nid))
    print(o[:900])
    print()
