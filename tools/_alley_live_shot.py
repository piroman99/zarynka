# -*- coding: utf-8 -*-
"""Живой кадр сцены «аллея» (узел 16, стр. 0) с новой скамейкой: телефон + десктоп.

Проверяет не «на глаз», а числами:
  * проп-скамейка загрузилась (naturalWidth) и целиком внутри сцены;
  * она реально красится — разница кадров «проп включён / выключен» > 0;
  * спрайт поэта не висит в воздухе: его низ и верх в ожидаемых местах.
Результат — PNG в `_sat/`.

Запуск: python3 tools/_alley_live_shot.py
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAT = os.path.join(ROOT, '_sat')
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402

URL = 'file://' + os.path.join(ROOT, 'vn2', 'index.html') + \
      '?node=16&page=0&instant=1&text=1&voice=0&music=0'

GEOM = r"""
(function(){
  function box(sel){
    var e = document.querySelector(sel); if(!e) return null;
    var r = e.getBoundingClientRect(); if(!r.width) return null;
    return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)];
  }
  var st = document.getElementById('stage').getBoundingClientRect();
  var p = document.querySelector('#props .prop');
  var poet = document.querySelector('.sprite.seated');
  var bg = document.querySelector('.bg.on');
  return {
    stage: [Math.round(st.left), Math.round(st.top), Math.round(st.width), Math.round(st.height)],
    bg: bg ? bg.style.backgroundImage : null,
    prop: box('#props .prop'),
    propOn: !!(p && p.classList.contains('on')),
    propNat: p ? [p.naturalWidth, p.naturalHeight] : null,
    poet: box('.sprite.seated'),
    poetOn: !!(poet && poet.classList.contains('on'))
  };
})()
"""


def run(name, w, h, dpr, mobile):
    b = Browser(w, h)
    try:
        b.send('Emulation.setDeviceMetricsOverride', width=w, height=h,
               deviceScaleFactor=dpr, mobile=mobile)
        b.navigate(URL, wait=3.0)
        b.wait_js("!!document.querySelector('#props .prop.on')", timeout=20)
        info = b.js(GEOM)
        shot = os.path.join(SAT, 'alley_live_%s.png' % name)
        b.shot(shot)
        # кадр без пропа — чтобы доказать, что скамейка действительно красится
        b.js("document.querySelector('#props .prop').style.display='none'")
        off = os.path.join(SAT, '_tmp_%s_noprop.png' % name)
        b.shot(off)
        # «чистый» кадр без интерфейса — для сверки с офлайн-композитом
        b.js("document.querySelector('#props .prop').style.display=''")
        b.js("['#vignette','#tools','#box','#chapter'].forEach(function(s){"
             "var e=document.querySelector(s); if(e) e.style.display='none';})")
        b.js("document.querySelector('#ovl').style.display='none'")
        clean = os.path.join(SAT, 'alley_clean_%s.png' % name)
        b.shot(clean)
        errs = b.errors()
    finally:
        b.close()
    a = np.asarray(Image.open(shot).convert('RGB'), np.int16)
    c = np.asarray(Image.open(off).convert('RGB'), np.int16)
    os.remove(off)
    diff = np.abs(a - c).mean(axis=2) > 12
    ys, xs = np.nonzero(diff)
    print('== %s %dx%d @%dx' % (name, w, h, dpr))
    for k, v in info.items():
        print('   %-8s %s' % (k, v))
    print('   пикселей скамейки (проп вкл/выкл): %d' % diff.sum())
    if diff.sum():
        print('   её рамка в кадре: x %d..%d, y %d..%d' % (xs.min(), xs.max(), ys.min(), ys.max()))
    print('   js-ошибок: %s' % (errs if errs else 'нет'))
    print('   кадр: %s' % os.path.relpath(shot, ROOT))
    print('   чистый: %s' % os.path.relpath(clean, ROOT))
    return shot, info


if __name__ == '__main__':
    run('phone', 390, 844, 2, True)
    run('desk', 1280, 720, 1, False)
