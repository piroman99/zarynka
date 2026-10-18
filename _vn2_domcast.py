# -*- coding: utf-8 -*-
"""DOM-дамп vn2: показывает, что движок реально поставил в #cast."""
import os, sys, glob, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
p = sys.argv[1] if len(sys.argv) > 1 else '1'
url = 'file://' + IDX + '?instant=1&node=9&page=%s&text=1&voice=0&music=0' % p
r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--virtual-time-budget=6000', '--dump-dom', url],
                   capture_output=True, text=True, timeout=120)
dom = r.stdout
m = re.search(r'<div id="cast".*?</div>\s*<', dom, re.S)
print('URL page', p)
print(m.group(0)[:1200] if m else 'cast not found')
print('--- log ---')
print(r.stderr[-500:])
