# -*- coding: utf-8 -*-
"""Полный DOM-дамп геометрии S4 (кадр с ТВ) при наезде."""
import os
import json
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

JS = r'''(() => {
  const R = (el) => { if (!el) return null; const b = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return {l: +b.left.toFixed(1), t: +b.top.toFixed(1), w: +b.width.toFixed(1),
            h: +b.height.toFixed(1), b: +b.bottom.toFixed(1), r: +b.right.toFixed(1),
            pos: cs.position, op: cs.opacity, zi: cs.zIndex, bg: cs.backgroundColor,
            tf: cs.transform, to: cs.transformOrigin}; };
  return {vw: innerWidth, vh: innerHeight,
          stage: R(document.getElementById('stage')),
          bgA: R(document.getElementById('bg-a')),
          bgB: R(document.getElementById('bg-b')),
          box: R(document.getElementById('box')),
          text: R(document.getElementById('text')),
          cls: document.getElementById('stage').className};
})()'''

b = Browser(1600, 900)
try:
    url = ('file://' + os.path.join(HERE, 'vn2', 'index.html')
           + '?node=5&text=1&voice=0&music=0&instant=1')
    b.navigate(url, wait=1.0)
    d = b.js(JS)
    for k, v in d.items():
        print(k, '=', v if not isinstance(v, dict) else json.dumps(v, ensure_ascii=False))
finally:
    b.close()
