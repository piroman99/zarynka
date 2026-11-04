# -*- coding: utf-8 -*-
"""Проверка набора букв титр-слоя (вариант B, 2026-11-04).

Гипотеза: буквы надписи (span внутри #ovl b) проявляются НЕ все сразу, а пропорционально
прочитанному подстрочнику; к концу страницы — все до одной.

Метод: headless-chrome, --virtual-time-budget в разных точках страницы, --dump-dom,
считаем span'ы с классом `in` (и `plain` при ?letters=0).
Ранний срез берётся как 40% длины подстрочника ЭТОЙ страницы (короткие фразы
допечатываются быстро — фиксированные 900 мс для них уже «конец»).
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
TYPE_MS = 14          # 18 * PACE(0.8) — как в app.js

data = json.loads(open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8')
                  .read().split('=', 1)[1].strip().rstrip(';'))
TX = {}
for _nd in data['nodes']:
    if _nd.get('t') == 'scene':
        for _j, _p in enumerate(_nd.get('pages', [])):
            TX[(_nd.get('id'), _j)] = _p.get('tx', '')


def early_ms(nid, p):
    return max(150, int(len(TX.get((nid, p), '')) * TYPE_MS * 0.4))


def dump(nid, p, budget, extra=''):
    q = ('auto=0&text=1&voice=0&music=0&node=%d&page=%d&%s' % (node_index(nid), p, extra))
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
                        '--disable-dev-shm-usage', '--hide-scrollbars',
                        '--window-size=1280,720',
                        '--virtual-time-budget=%d' % budget,
                        '--dump-dom', 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=240)
    return r.stdout


def counts(dom):
    i = dom.find('id="ovl"')
    j = dom.find('<div id="trans', i) if i >= 0 else -1
    inner = dom[i:j if j > i else len(dom)] if i >= 0 else ''
    spans = re.findall(r'<span([^>]*)>([^<]*)</span>', inner)
    total = len(spans)
    shown = sum(1 for attrs, _ in spans
                if 'class="in"' in attrs or 'class="plain"' in attrs)
    txt = ''.join(t for _, t in spans)
    return total, shown, txt


bad = 0
for nid, p in WANT:
    early = early_ms(nid, p)
    e_total, e_shown, e_txt = counts(dump(nid, p, early))
    l_total, l_shown, l_txt = counts(dump(nid, p, 20000))
    ok = True
    why = []
    if e_total == 0:
        ok = False
        why.append('нет span-букв')
    if e_total != l_total:
        ok = False
        why.append('букв %d/%d' % (e_total, l_total))
    if l_shown != l_total:
        ok = False
        why.append('в конце показано %d из %d' % (l_shown, l_total))
    if e_shown >= l_total:
        ok = False
        why.append('в начале уже всё на экране (%d)' % e_shown)
    print('%-4s стр.%d  букв %2d  на %4d мс: %2d  на 20 с: %2d  %s'
          % (nid, p + 1, l_total, early, e_shown, l_shown,
             'OK' if ok else 'ПРОБЛЕМА: ' + '; '.join(why)))
    if not ok:
        bad += 1
    print('     текст: %r' % l_txt)

# ?letters=0 — буквы есть, но без анимации (класс plain) и сразу все
t0, s0, _ = counts(dump('s3', 0, 300, 'letters=0&instant=0'))
print('\nletters=0 (300 мс): букв %d, показано %d' % (t0, s0))
if t0 == 0 or s0 != t0:
    print('ПРОБЛЕМА: letters=0 должен показывать строку целиком сразу')
    bad += 1

print('\nпроблем: %d' % bad)
sys.exit(1 if bad else 0)
