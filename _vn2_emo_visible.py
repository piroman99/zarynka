# -*- coding: utf-8 -*-
"""Точечная проверка: движок показывает ровно заявленный файл эмоции (видимые спрайты).

`_vn2_emo_verify.py` сверяет DOM целиком, а в DOM остаются скрытые (opacity 0) img от
предыдущей страницы — поэтому он врёт. Здесь читаем только ВИДИМЫЕ спрайты (opacity>0.5)
через CDP и сверяем с content.js.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
CH = D['chars']
REC = node_index('reception')

GEO = """(() => {
  const out = {};
  document.querySelectorAll('#cast .sprite').forEach(s => {
    const op = parseFloat(getComputedStyle(s).opacity);
    if (op > 0.5) out[s.dataset.slot] = s.getAttribute('src');
  });
  return out;
})()"""

b = Browser(1280, 720)
ok = fail = 0
try:
    for i, pg in enumerate(rec['pages']):
        exp = {}
        for slot, key in (('0', 'l'), ('1', 'r')):
            c = (pg.get('cast') or {}).get(key)
            if not c:
                continue
            who, emo = c
            u = ((CH.get(who) or {}).get('emos') or {}).get(emo)
            if u:
                exp[slot] = u
        b.navigate('file://' + os.path.join(HERE, 'vn2', 'index.html')
                   + '?instant=1&node=%d&page=%d&text=1&voice=0&music=0&auto=0' % (REC, i),
                   wait=0.9)
        got = b.js(GEO)
        good = got == exp
        ok += good
        fail += (not good)
        if not good:
            print('%02d РАСХОЖДЕНИЕ: ждали %s, видно %s' % (i, exp, got))
finally:
    b.close()

print('\nстраниц: %d  OK=%d FAIL=%d' % (len(rec['pages']), ok, fail))
