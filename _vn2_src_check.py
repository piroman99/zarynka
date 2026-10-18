# -*- coding: utf-8 -*-
"""Проверка src спрайтов по страницам: какие файлы реально стоят в слотах."""
import os, glob, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')

for p in (0, 1, 3, 6, 18, 32, 49, 50):
    url = ('file://' + IDX + '?instant=1&node=9&page=%d&text=1&voice=0&music=0' % p)
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--virtual-time-budget=5000', '--dump-dom', url],
                       capture_output=True, text=True, timeout=120)
    m = re.search(r'<div id="cast".*?</div>', r.stdout, re.S)
    blk = m.group(0) if m else ''
    srcs = re.findall(r'data-slot="(\d)"[^>]*?src="([^"]*)"', blk)
    print('page %02d -> %s' % (p, srcs or 'нет спрайтов'))
