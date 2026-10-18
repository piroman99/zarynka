# -*- coding: utf-8 -*-
"""Проверка: Старик попал в chars/cast + скриншот приёмной стр.0 и стр.1."""
import os, json, glob, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]

s = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
d = json.loads(s[s.index('window.VN =') + len('window.VN ='):].rstrip().rstrip(';'))
print('chars:', {k: list(v['emos']) for k, v in d['chars'].items()})
rec = [n for n in d['nodes'] if n.get('id') == 'reception'][0]
for k in range(0, 4):
    p = rec['pages'][k]
    print(' page', k, '| who=', p.get('who'), '| cast=', p['cast'])

OUT = os.path.join(HERE, 'assets', 'review')
base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
for pg in (0, 1):
    out = os.path.join(OUT, 'review_132_reception_p%d.png' % pg)
    url = base + '?node=9&page=%d&instant=1&text=1&voice=0&music=0' % pg
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--window-size=1600,900',
                    '--virtual-time-budget=3000', '--screenshot=' + out, url], check=True)
    print('shot page', pg, '->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
