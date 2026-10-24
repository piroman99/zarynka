# -*- coding: utf-8 -*-
"""Регресс на повторный запуск: после прохождения серии «В меню» -> «Начать»
должно работать столько раз, сколько нужно (раньше молчало: start() упирался
в started=true, жив был только «Тизер»).
"""
import os, sys, time, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

ok = True
def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK   ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))

SHOW = "(function(){var e=document.getElementById('%s');return !!e&&e.classList.contains('show')})()"
VLAYER_OFF = "document.getElementById('vlayer').hidden"
CLICK = "document.getElementById('%s').click()"

b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900, deviceScaleFactor=1, mobile=False)
    b.navigate(BASE + '?preload=0')
    time.sleep(1.0)
    check('титул показан', b.js(SHOW % 'title'))

    for run in (1, 2, 3):
        b.js(CLICK % 'start')
        time.sleep(0.9)
        check('прогон %d: титул скрылся' % run, not b.js(SHOW % 'title'))
        check('прогон %d: значок пошёл' % run, b.js(VLAYER_OFF) == False)
        b.js(CLICK % 'vskip')
        time.sleep(0.5)
        # с 2026-10-24 после значка идёт посвящение — закрываем его, как это сделал бы игрок
        b.js(CLICK % 'ded')
        time.sleep(0.5)
        check('прогон %d: страница 0' % run, b.js("__DBG.pos") == 0, b.js("__DBG.pos"))
        check('прогон %d: HUD включён' % run, b.js("document.getElementById('hud').classList.contains('on')"))
        n = b.js("""(function(){
          var st=document.getElementById('stage'), i=0;
          for(; i<500; i++){
            if(document.getElementById('end').classList.contains('show')) break;
            if(document.getElementById('credits').classList.contains('show')){
              document.getElementById('cr-skip').click(); continue;
            }
            st.click();
          }
          return i;
        })()""")
        time.sleep(0.4)
        check('прогон %d: дошли до конца' % run, b.js(SHOW % 'end'), 'кликов ' + str(n))
        b.js(CLICK % 'e-menu')
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
    srv.shutdown()

print('\nИТОГ:', 'ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОВАЛЫ')
sys.exit(0 if ok else 1)
