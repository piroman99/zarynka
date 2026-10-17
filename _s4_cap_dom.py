# -*- coding: utf-8 -*-
"""DOM-замер S4: где плашка-подпись относительно #box на наезде и до него."""
import os
import json
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

# доля кадра, которую занимает плашка (из _prolog_finals.build('s4'), 2400x1350)
CX0, CY0, CX1, CY1 = 862 / 2400.0, 684 / 1350.0, 1535 / 2400.0, 762 / 1350.0

JS = '''(() => {
  const r = (el) => { const b = el.getBoundingClientRect();
    return {l:b.left, t:b.top, w:b.width, h:b.height, b:b.bottom}; };
  const on = [document.getElementById('bg-a'), document.getElementById('bg-b')]
            .filter(e => e && getComputedStyle(e).opacity > 0.5);
  const st = document.getElementById('stage');
  const box = document.getElementById('box');
  return {stage: r(st), box: r(box), text: r(document.getElementById('text')),
          bg: on.length ? r(on[0]) : null,
          tf: on.length ? on[0].style.transform : null,
          to: on.length ? on[0].style.transformOrigin : null,
          vh: innerHeight, vw: innerWidth};
})()'''

for tag, extra in (('zoom', '&instant=1'), ('wide', '')):
    b = Browser(1600, 900)
    try:
        url = 'file://' + os.path.join(HERE, 'vn2', 'index.html') + '?node=5&text=1&voice=0&music=0' + extra
        b.navigate(url, wait=0.6)
        b.wait_js("!!document.querySelector('#bg-a, #bg-b')")
        d = b.js(JS)
        bg = d['bg']
        cap = dict(l=bg['l'] + CX0 * bg['w'], t=bg['t'] + CY0 * bg['h'],
                   r=bg['l'] + CX1 * bg['w'], b=bg['t'] + CY1 * bg['h'])
        print('== %s ==' % tag)
        print('  transform=%s origin=%s' % (d['tf'], d['to']))
        print('  stage h=%.0f  bg rect w=%.0f h=%.0f' % (d['stage']['h'], bg['w'], bg['h']))
        print('  плашка: x %.0f..%.0f  y %.0f..%.0f  (h=%.0f px)' %
              (cap['l'], cap['r'], cap['t'], cap['b'], cap['b'] - cap['t']))
        print('  #box:   верх %.0f  (#text верх %.0f)' % (d['box']['t'], d['text']['t']))
        print('  зазор плашка->#box: %.0f px' % (d['box']['t'] - cap['b']))
        print('  плашка внутри сцены: %s (сцена %.0f..%.0f)' %
              (cap['t'] >= d['stage']['t'] - 1 and cap['b'] <= d['stage']['b'] + 1,
               d['stage']['t'], d['stage']['b']))
        print('  высота строки текста ≈ %.0f px при ширине окна %d' % ((cap['b'] - cap['t']) * 0.55, d['vw']))
        errs = b.errors()
        print('  JS-ошибки:', errs if errs else 'нет')
    finally:
        b.close()
