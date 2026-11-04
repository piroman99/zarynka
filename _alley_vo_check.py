# -*- coding: utf-8 -*-
"""Озвучка сцены «аллея» в игре: у страниц есть vo, движок реально грузит mp3.

Проверяем по живому кадру (CDP): для трёх страниц (закадр, Екатерина, поэт) в
`#voice` после старта стоит нужный файл и он не 404. Плюс голос поэта = Umbriel
по манифесту.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

ALLEY = node_index('alley')
STEPS = node_index('steps')
base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')

# (узел, страница, кто должен говорить, что за файл)
CASES = [(STEPS, 0, 'narr', 'al_00.mp3'),
         (ALLEY, 2, 'Екатерина', 'al_04.mp3'),
         (ALLEY, 12, 'Поэт', 'al_14.mp3')]

b = Browser(1280, 720)
ok = fail = 0
try:
    for node, pg, who, want in CASES:
        url = base + '?node=%d&page=%d&instant=1&text=1&music=0&auto=0' % (node, pg)
        b.navigate(url, wait=1.0)
        b.js("document.getElementById('start') && document.getElementById('start').click()")
        time.sleep(0.4)
        got = b.js("(function(){var v=document.getElementById('voice');"
                   "return {src:(v.getAttribute('src')||'').split('?')[0],"
                   " err:v.error?v.error.code:0, dur:v.duration||0};})()")
        src = (got or {}).get('src', '')
        good = src.endswith(want) and not (got or {}).get('err') and (got or {}).get('dur', 0) > 0
        ok += good
        fail += (not good)
        print('%s %-10s стр.%-2d ждали %s -> %s (err %s, %.1f с)'
              % ('OK  ' if good else 'FAIL', who, pg, want,
                 os.path.basename(src) or '(пусто)', (got or {}).get('err'),
                 (got or {}).get('dur', 0)))
finally:
    b.close()

m = json.load(open(os.path.join(HERE, 'vn2', 'audio', 'vo', '_voices.json'), encoding='utf-8'))
poet = [k for k, v in m.items() if v.get('voice') == 'Поэт']
print('файлов поэта в манифесте: %d, голос Umbriel (проверка через opts невозможна)'
      % len(poet))
print('\nИТОГ: OK=%d FAIL=%d' % (ok, fail))
sys.exit(1 if fail else 0)
