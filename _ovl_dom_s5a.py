# -*- coding: utf-8 -*-
"""Точная проверка геометрии плашки кадра 11 через DOM: inline-стили #ovl i в em
(1em = ширина кадра 2400). Сверяем с целевой панелью 1119,505,1848,890."""
import os
import re
import glob
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

TARGET = (1119, 505, 1848, 890)
E = 2400.0


def px(v):
    m = re.match(r'(-?[\d.]+)em', v.strip())
    return 0.0 if not m else float(m.group(1)) * E


for p in (0, 1):
    q = ('instant=1&auto=0&pause=1&pace=0&node=%d&page=%d&text=1&voice=0&music=0'
         % (node_index('s5a'), p))
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
                        '--disable-dev-shm-usage', '--hide-scrollbars',
                        '--window-size=1280,720', '--virtual-time-budget=6000',
                        '--dump-dom', 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=180)
    dom = r.stdout
    m = re.search(r'<div id="ovl"[^>]*class="([^"]*)"(.*?)</div>', dom, re.S)
    if not m:
        print('page', p, 'NO #ovl')
        continue
    cls, inner = m.group(1), m.group(2)
    its = re.findall(r'<i style="([^"]*)"></i>', inner)
    txts = re.findall(r'<b style="([^"]*)">([^<]*)</b>', inner)
    print('page', p, 'classes=', cls.strip(), 'plates=', len(its), 'texts=', len(txts))
    for st in its:
        d = dict((k.strip(), v) for k, v in (kv.split(':', 1) for kv in st.split(';') if ':' in kv))
        x0 = px(d.get('left', '0'))
        y0 = px(d.get('top', '0'))
        x1 = x0 + px(d.get('width', '0'))
        y1 = y0 + px(d.get('height', '0'))
        got = tuple(round(v) for v in (x0, y0, x1, y1))
        ok = all(abs(got[i] - TARGET[i]) <= 2 for i in range(4))
        print('   plate', got, 'target', TARGET, 'OK' if ok else 'MISMATCH',
              'bg=', d.get('background', '').strip()[:40])
    for st, t in txts:
        d = dict((k.strip(), v) for k, v in (kv.split(':', 1) for kv in st.split(';') if ':' in kv))
        print('   text %-24r size=%.0f x=%.0f y=%.0f color=%s'
              % (t, px(d.get('font-size', '0')), px(d.get('left', '0')),
                 px(d.get('top', '0')), d.get('color', '').strip()))
