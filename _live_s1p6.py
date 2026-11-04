# -*- coding: utf-8 -*-
"""Живая проверка: p6[0] = Марс, p6[1] = лунная база, s1[0] = стена, s1[1] = подворотня.

    python3 _live_s1p6.py   (обновлённые ожидания)
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

BASE = 'https://piroman99.github.io/zarynka/vn2/index.html'
GEO = """
(function(){
  var el=[].filter.call(document.querySelectorAll('.bg'),function(e){
      return getComputedStyle(e).opacity>0.5;})[0];
  var u=el?(getComputedStyle(el).backgroundImage||''):'';
  return {bg:u.split('/').pop().replace(/["')]/g,''), tx:(document.getElementById('text')||{}).textContent||''};
})()
"""
CHECKS = [('s1[0] стена', 'node=3&page=0', 's1a.webp'),
          ('s1[1] подворотня', 'node=3&page=1', 's1.webp'),
          ('p6[0] Марс', 'node=4&page=0', 'p6.webp'),
          ('p6[1] лунная база', 'node=4&page=1', 'p6luna.webp')]

bad = 0
b = Browser(1280, 720)
try:
    for name, q, want in CHECKS:
        b.navigate(BASE + '?instant=1&auto=0&text=1&voice=0&music=0&' + q, wait=3.0)
        time.sleep(0.6)
        g = b.js(GEO)
        ok = g.get('bg') == want
        bad += 0 if ok else 1
        print('%s %-20s bg=%-14s %s' % ('OK  ' if ok else 'FAIL', name, g.get('bg'),
                                        g.get('tx', '')[:58]))
    errs = [e for e in b.errors() if 'favicon' not in e]
    print('js-ошибок: %d %s' % (len(errs), errs[:2]))
finally:
    b.close()
print('ИТОГ:', 'ВСЁ ЗЕЛЁНОЕ' if bad == 0 else 'ПРОБЛЕМЫ: %d' % bad)
