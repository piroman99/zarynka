# -*- coding: utf-8 -*-
"""Замер спрайта Старика в движке: где стоит, какого размера, влезает ли в кадр.
Сравниваем стр.0 (Сергей) и стр.1 (Старик) узла reception.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

JS = '''(() => {
  const r = (el) => { const b = el.getBoundingClientRect();
    return {l: Math.round(b.left), t: Math.round(b.top), w: Math.round(b.width),
            h: Math.round(b.height), b: Math.round(b.bottom), r: Math.round(b.right)}; };
  const imgs = [...document.querySelectorAll('#cast .sprite')].map(e => ({
      src: (e.getAttribute('src') || '').split('/').pop(), rect: r(e),
      nat: [e.naturalWidth, e.naturalHeight], op: getComputedStyle(e).opacity,
      cls: e.className, id: e.id }));
  return {vh: innerHeight, vw: innerWidth, stage: r(document.getElementById('stage')),
          box: r(document.getElementById('box')), imgs: imgs};
})()'''

base = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
for pg in (0, 1):
    b = Browser(1600, 900)
    b.navigate(base + '?node=9&page=%d&instant=1&text=1&voice=0&music=0' % pg, wait=3)
    d = b.js(JS)
    print('--- page', pg, 'viewport', d['vw'], 'x', d['vh'])
    print('    stage', d['stage'])
    print('    box  ', d['box'])
    for im in d['imgs']:
        print('    img', im['src'], 'rect', im['rect'], 'nat', im['nat'], 'op', im['op'])
    b.close()
