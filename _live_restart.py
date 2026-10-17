# -*- coding: utf-8 -*-
"""Живая проверка на GitHub Pages: «пройти -> В меню -> Начать» работает повторно."""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

BASE = 'https://piroman99.github.io/zarynka/vn2/index.html?preload=0'
ok = True
def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK   ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))

SHOW = "(function(){var e=document.getElementById('%s');return !!e&&e.classList.contains('show')})()"
b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900, deviceScaleFactor=1, mobile=False)
    b.navigate(BASE)
    if not b.wait_js("!!window.__DBG", timeout=60):
        check('движок поднялся', False); raise SystemExit(1)
    check('титул показан', b.js(SHOW % 'title'))

    for run in (1, 2):
        b.js("document.getElementById('start').click()")
        time.sleep(0.9)
        check('прогон %d: титул скрылся' % run, not b.js(SHOW % 'title'))
        b.js("document.getElementById('vskip').click()")
        time.sleep(0.6)
        check('прогон %d: страница 0' % run, b.js("__DBG.pos") == 0, b.js("__DBG.pos"))
        n = b.js("""(function(){
          var st=document.getElementById('stage'), i=0;
          for(; i<500; i++){
            if(document.getElementById('end').classList.contains('show')) break;
            st.click();
          }
          return i;
        })()""")
        time.sleep(0.4)
        check('прогон %d: дошли до конца' % run, b.js(SHOW % 'end'), 'кликов ' + str(n))
        b.js("document.getElementById('e-menu').click()")
        time.sleep(0.4)
        check('прогон %d: меню показано' % run, b.js(SHOW % 'title'))
        check('прогон %d: кнопка «Начать»' % run, b.js("document.getElementById('start').textContent") == 'Начать',
              b.js("document.getElementById('start').textContent"))

    errs = b.errors()
    check('js-ошибок нет', not errs, ' | '.join(errs)[:300])
finally:
    try:
        b.close()
    except Exception:
        pass

print('\nИТОГ:', 'ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОВАЛЫ')
sys.exit(0 if ok else 1)
