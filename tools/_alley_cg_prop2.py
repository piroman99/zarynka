# -*- coding: utf-8 -*-
"""CG «Муза» v5 A: на странице с репликой «— Муза, — юноша покраснел и отвернулся»
фон = img/cg/al_muza.webp, спрайтов и пропа-скамейки нет; на соседних страницах — фон
аллеи, проп виден. Индекс страницы берём из content.js, а не из головы.

Запуск: python3 tools/_alley_cg_prop2.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

BASE = 'file://' + os.path.join(ROOT, 'vn2', 'index.html')
PROP_ON = ("(function(){var p=document.querySelector('#props .prop');"
           "return !!(p && p.classList.contains('on'));})()")
GEO = """
(function(){
  var b=document.querySelector('.bg.on');
  var sp=[].filter.call(document.querySelectorAll('.sprite'),
        function(e){return getComputedStyle(e).opacity!=='0';}).length;
  return {bg:b?b.style.backgroundImage:'', prop:!!(document.querySelector('#props .prop')||{}).classList &&
          document.querySelector('#props .prop').classList.contains('on'),
          sprites:sp, tx:(document.getElementById('text').textContent||'').trim().slice(0,40)};
})()
"""

# какой индекс у страницы с «покраснел и отвернулся» — по content.js
import json
import re
src = open(os.path.join(ROOT, 'vn2', 'content.js'), encoding='utf-8').read()
m = re.search(r'window\.VN\s*=\s*(\{.*\})\s*;?\s*$', src, re.S)
D = json.loads(m.group(1))
AL = node_index('alley')
pages = D['nodes'][AL]['pages']
idx = [i for i, p in enumerate(pages) if 'покраснел и отвернулся' in p.get('tx', '')]
print('аллея = node=%d, страниц %d, CG-страница(0-based) = %s' % (AL, len(pages), idx))
cg = idx[0]

b = Browser(1280, 720)
ok = fail = 0
try:
    for i in (cg - 1, cg, cg + 1):
        # page-параметр совпадает с индексом страницы (проверено сканом _alley_page_scan.py)
        b.navigate(BASE + '?node=%d&page=%d&instant=1&auto=0&text=1&voice=0&music=0' % (AL, i), wait=2.5)
        b.wait_js("(document.querySelector('.bg.on')||{}).style.backgroundImage !== ''", timeout=20)
        g = b.js(GEO)
        want_cg = (i == cg)
        if want_cg:
            good = ('al_muza.webp' in g['bg']) and (not g['prop']) and g['sprites'] == 0
        else:
            good = ('alley.webp' in g['bg']) and g['prop'] and g['sprites'] == 2
        ok += 1 if good else 0
        fail += 0 if good else 1
        print('стр.%2d %-28s проп=%-5s спрайтов=%d  %s  %r'
              % (i, g['bg'][:28], g['prop'], g['sprites'], 'OK' if good else '!!!', g['tx']))
finally:
    b.close()

print('\nИТОГ: OK=%d FAIL=%d' % (ok, fail))
sys.exit(1 if fail else 0)
