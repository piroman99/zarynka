# -*- coding: utf-8 -*-
"""Живая проверка (исправленная): спрайты и CG-кадр на демо, без падения на #bg."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

ALLEY = node_index('alley')
URL = ('https://piroman99.github.io/zarynka/vn2/index.html'
       '?instant=1&text=1&voice=0&music=0&auto=0&node=%d&page=%d')
GEO = """(() => {
  const sp = [...document.querySelectorAll('#cast .sprite')].map(s => ({
      src: (s.getAttribute('src')||'').split('/').pop(),
      op: getComputedStyle(s).opacity,
      h: Math.round(s.getBoundingClientRect().height)})).filter(x => parseFloat(x.op) > 0.5);
  const bgs = [...document.querySelectorAll('div')]
      .map(d => getComputedStyle(d).backgroundImage)
      .filter(u => u && u !== 'none');
  return {sprites: sp, bgs: bgs.map(u => (u.match(/url\\("?([^")]+)"?\\)/)||[])[1] || u)};
})()"""

b = Browser(1600, 900)
try:
    for pg in (0, 18, 38):
        b.navigate(URL % (ALLEY, pg), wait=3.5)
        g = b.js(GEO) or {}
        print('стр.%-2d спрайты %s' % (pg, json.dumps(g.get('sprites'), ensure_ascii=False)))
        for u in g.get('bgs', [])[:3]:
            if 'webp' in u:
                print('        фон:', u.split('/')[-1])
    print('js-ошибок:', len(b.errors()), b.errors()[:2])
finally:
    b.close()
