# -*- coding: utf-8 -*-
"""Тишина на длинном переходе: голос новой сцены НЕ должен читать под жетоном.

Меряет по времени: затемнение, жетон, осветление и момент, когда у #voice
появился src и пошло воспроизведение. Требуется: голос стартует после конца
осветления, тишина — не меньше длины перехода.
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
import _vo_util as U


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT
NODE = {n.get('id'): i for i, n in enumerate(U.load_content()['nodes'])}

ok = True


def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK   ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))


b = Browser(1280, 720)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1280, height=720,
           deviceScaleFactor=1, mobile=False)
    b.navigate(BASE + '?node=%d&preload=0' % NODE['s7'])
    time.sleep(1.5)
    # дойти до последней страницы пролога: там голос уже звучит.
    # t0 = момент КЛИКА, который запустил переход (а не момент, когда мы его заметили).
    t0 = None
    for _ in range(6):
        tc = time.time()
        b.js("document.getElementById('stage').click()")
        time.sleep(0.2)
        if b.js("document.getElementById('trans').classList.contains('on')"):
            t0 = tc
            break
    if t0 is None:
        t0 = time.time()
    t_on = t_logo = t_off = t_voice = None
    while time.time() - t0 < 6.0:
        st = b.js("""(function(){
          var tr=document.getElementById('trans'), lg=document.getElementById('translogo');
          var v=document.getElementById('voice');
          return [tr.classList.contains('on'), lg.classList.contains('on'),
                  (v.getAttribute('src')||''), v.paused, __DBG.node];
        })()""")
        el = time.time() - t0
        if st[0] and t_on is None:
            t_on = el
        if st[1] and t_logo is None:
            t_logo = el
        if t_on is not None and not st[0] and t_off is None:
            t_off = el
        if st[2] and not st[3] and t_voice is None:
            t_voice = el
        if t_voice is not None and t_off is not None:
            break
        time.sleep(0.05)
    print('  затемнение с %.2f, жетон с %.2f, светло с %.2f, голос с %s'
          % (t_on or -1, t_logo or -1, t_off if t_off is not None else -1,
             '%.2f' % t_voice if t_voice is not None else 'не зазвучал'))
    check('переход начался', t_on is not None)
    check('голос зазвучал', t_voice is not None)
    if t_voice is not None and t_off is not None:
        check('голос НЕ звучит под жетоном (старт после осветления)',
              t_voice >= t_off - 0.05, 'голос %.2f, светло %.2f' % (t_voice, t_off))
        # Иван 2026-10-21: «слишком короткая пауза, сделай общую длину 4 секунды»
        check('тишина на переходе ≈4 с (3.85…4.25)', 3.85 <= t_voice <= 4.25,
              '%.2f с' % t_voice)
    check('js-ошибок нет', not b.errors(), b.errors())

    # --- клик во время перехода = сразу дальше, голос не ждёт ---
    b.navigate(BASE + '?node=%d&preload=0' % NODE['s7'])
    time.sleep(1.6)
    print('  после перезагрузки: pos=%s node=%s typing=%s'
          % (b.js('__DBG.pos'), b.js('__DBG.node'), b.js('__DBG.typing')))
    for k in range(6):
        b.js("document.getElementById('stage').click()")
        time.sleep(0.2)
        st = b.js("[document.getElementById('trans').classList.contains('on'),"
                  " __DBG.pos, __DBG.node]")
        print('  клик %d -> %s' % (k, st))
        if st[0]:
            break
    b.js("document.getElementById('stage').click()")     # пропустить переход
    time.sleep(0.4)
    st = b.js("[document.getElementById('trans').classList.contains('on'),"
              " (document.getElementById('voice').getAttribute('src')||''),"
              " document.getElementById('voice').paused, __DBG.node]")
    print('  после пропуска: trans=%s src=%s paused=%s node=%s'
          % (st[0], st[1][-20:] or '-', st[2], st[3]))
    check('клик снял затемнение', st[0] is False)
    check('после клика голос сразу играет', bool(st[1]) and st[2] is False,
          'src=%s paused=%s' % (st[1][-18:], st[2]))

    # --- авто-режим не застревает на отложенном голосе ---
    b.navigate(BASE + '?node=%d&preload=0&auto=1' % NODE['s7'])
    time.sleep(1.5)
    start_pos = b.js('__DBG.pos')
    moved = None
    t1 = time.time()
    while time.time() - t1 < 30:
        p = b.js('__DBG.pos')
        if p is not None and p > start_pos:      # перелистнул через переход
            moved = time.time() - t1
            break
        time.sleep(0.4)
    check('авто-режим листает через переход', moved is not None,
          '%.1f с' % moved if moved else 'не сдвинулся')
    # и голос новой сцены в авто-режиме тоже звучит
    spoke = None
    t2 = time.time()
    while time.time() - t2 < 15:
        st = b.js("[(document.getElementById('voice').getAttribute('src')||''),"
                  " document.getElementById('voice').paused]")
        if 'rec_00' in st[0] and st[1] is False:
            spoke = time.time() - t2
            break
        time.sleep(0.4)
    check('в авто-режиме голос кабинета звучит', spoke is not None,
          '%.1f с' % spoke if spoke else 'не зазвучал')
    check('js-ошибок нет (после всех шагов)', not b.errors(), b.errors())
finally:
    b.close()

print('\nИТОГ: ' + ('ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(0 if ok else 1)
