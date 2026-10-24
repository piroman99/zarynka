# -*- coding: utf-8 -*-
"""Проверка стартового экрана и мобильных удобств:
  1) «титры» (заголовок/подзаголовок/эпизод/автор) на старте СКРЫТЫ, кнопка есть;
  2) ?titles=1 возвращает надписи;
  3) по кнопке «Начать» запрашивается фуллскрин и wake lock (в тестовом Chromium
     автозапуск разрешён, поэтому фуллскрин может не встать — проверяем, что код
     ПЫТАЕТСЯ и ничего не ломается);
  4) wake lock берётся и снимается (по видимости и в конце серии).
"""
import os
import sys
import time
import threading
import functools
import http.server
import socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

ok = True


def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK   ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT
VIS = ("(function(){var e=document.getElementById('%s');"
       "return getComputedStyle(e).display!=='none'})()")

b = Browser(1280, 720)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1280, height=720,
           deviceScaleFactor=1, mobile=False)

    # --- 1) старт без титров ---
    b.navigate(BASE + '?preload=0')
    time.sleep(1.2)
    check('стартовый экран показан',
          b.js("document.getElementById('title').classList.contains('show')"))
    check('заголовок «ЗАРЯНКА» скрыт', b.js(VIS % 'tt') is False)
    check('подзаголовок скрыт',
          b.js("getComputedStyle(document.querySelector('#title .sub')).display") == 'none')
    check('эпизод скрыт',
          b.js("getComputedStyle(document.getElementById('tep')).display") == 'none')
    check('автор скрыт',
          b.js("getComputedStyle(document.getElementById('byline')).display") == 'none')
    check('логотип виден',
          b.js("getComputedStyle(document.querySelector('#title .logo')).display") != 'none')
    check('кнопка «Начать» видна',
          b.js("getComputedStyle(document.getElementById('start')).display") != 'none')

    # --- 2) ?titles=1 ---
    b.navigate(BASE + '?preload=0&titles=1')
    time.sleep(1.2)
    check('?titles=1 возвращает заголовок', b.js(VIS % 'tt') is True)
    check('?titles=1 возвращает автора',
          b.js("getComputedStyle(document.getElementById('byline')).display") != 'none')

    # --- 3) старт: фуллскрин + wake lock ---
    b.navigate(BASE + '?preload=0')
    time.sleep(1.2)
    check('wake lock доступен в этом браузере',
          b.js("__DBG.wake.ok") is True, b.js("__DBG.wake"))
    b.js("document.getElementById('start').click()")
    time.sleep(1.5)
    w = b.js("__DBG.wake")
    check('после старта wake lock запрошен', w.get('want') is True, w)
    check('wake lock взят', w.get('held') is True, w)
    # В headless-хроме фуллскрин запрещён (TypeError: Permissions check failed),
    # поэтому проверяем, что код ЕГО ЗАПРОСИЛ и старт не сломался.
    check('фуллскрин запрошен по кнопке', b.js('__DBG.fsTried') == 1,
          'fsTried=%s, fs=%s' % (b.js('__DBG.fsTried'), b.js('__DBG.fs')))
    check('значок пошёл (старт не сломан)',
          b.js("document.getElementById('vlayer').hidden") is False)
    check('js-ошибок нет', not b.errors(), b.errors())

    # --- 4) конец серии снимает wake lock ---
    b.js("document.getElementById('vskip').click()")
    time.sleep(0.4)
    b.js("""(function(){var st=document.getElementById('stage');
      for(var i=0;i<600;i++){
        if(document.getElementById('end').classList.contains('show')) break;
        // с 2026-10-24 после серии сначала идёт ролл титров — его тоже пропускаем
        if(document.getElementById('credits').classList.contains('show')){
          document.getElementById('cr-skip').click(); continue;
        }
        st.click();
      }
    })()""")
    time.sleep(0.8)
    check('дошли до конца серии',
          b.js("document.getElementById('end').classList.contains('show')"))
    w = b.js("__DBG.wake")
    check('в конце серии wake lock снят', w.get('want') is False and w.get('held') is False, w)
finally:
    b.close()

print('\nИТОГ: ' + ('ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(0 if ok else 1)
