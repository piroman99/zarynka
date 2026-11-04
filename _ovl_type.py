# -*- coding: utf-8 -*-
"""Проверка «строка надписи появляется на своей фразе» — по DOM, без ожидания.

?ovlp=P (тест-хук) ставит прогресс страницы в P: строки с at <= P должны стоять ЦЕЛИКОМ,
строки с at > P — не показывать ни одной буквы. Так проверяем саму раскладку по фразам
(тайминг под озвучку меряется отдельно — `_ovl_phrase_probe.py`, на реальном времени).
"""
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

WANT = [('s3', 0), ('s4', 0), ('s5a', 0), ('s5a', 1), ('s5b', 0)]

data = json.loads(open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8')
                  .read().split('=', 1)[1].strip().rstrip(';'))
PAGES = {}
for nd in data['nodes']:
    if nd.get('t') == 'scene':
        for j, p in enumerate(nd.get('pages', [])):
            PAGES[(nd.get('id'), j)] = p


def dump(nid, p, extra):
    q = ('auto=0&text=1&voice=0&music=0&node=%d&page=%d&%s' % (node_index(nid), p, extra))
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
                        '--disable-dev-shm-usage', '--hide-scrollbars',
                        '--window-size=1280,720', '--virtual-time-budget=4000',
                        '--dump-dom', 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=180)
    return r.stdout


def lines_state(dom):
    """[ (букв всего, показано), ... ] по строкам #ovl b в порядке вставки."""
    i = dom.find('id="ovl"')
    j = dom.find('<div id="trans', i) if i >= 0 else -1
    inner = dom[i:j if j > i else len(dom)] if i >= 0 else ''
    out = []
    for body in re.findall(r'<b style="[^"]*">(.*?)</b>', inner, re.S):
        spans = re.findall(r'<span([^>]*)>', body)
        shown = sum(1 for a in spans if 'class="in"' in a or 'class="plain"' in a)
        out.append((len(spans), shown))
    return out


bad = 0
for nid, p in WANT:
    pg = PAGES.get((nid, p)) or {}
    ats = [it['at'] for it in (pg.get('ovl') or []) if 't' in it]
    # три среза: до первой фразы, в середине, в конце
    for prog, label in ((0.05, '0.05'), (0.5, '0.50'), (1.0, '1.00')):
        st = lines_state(dump(nid, p, 'ovlp=%s' % prog))
        exp = [(n, n if at <= prog else 0) for (n, _), at in zip(st, ats)]
        ok = st == exp
        print('%-4s стр.%d ovlp=%s  строки %s  ожидалось %s  %s'
              % (nid, p + 1, label, st, exp, 'OK' if ok else 'ПРОБЛЕМА'))
        if not ok:
            bad += 1

# ?letters=0 — без анимации, но раскладка по фразам та же (всё, что разрешено прогрессом)
st = lines_state(dump('s3', 0, 'letters=0&ovlp=0.5'))
print('\nletters=0&ovlp=0.5: %s' % (st,))

print('\nпроблем: %d' % bad)
sys.exit(1 if bad else 0)
