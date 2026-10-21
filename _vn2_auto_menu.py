# -*- coding: utf-8 -*-
"""Регресс: «Авто» в меню не должен запускать новеллу и глотать видео с жетоном.

Баг (Иван 2026-10-21): на титуле нажимаешь «Авто» — сразу переключается на кадр
с подворотней, минуя значок-видео, и первая страница пролога пропускается.

Проверяем:
  1) «Авто» на титуле ничего не листает (титул на месте, значка нет, pos = 0);
  2) после «Начать» идёт значок-видео (не сразу страница);
  3) авто-режим включён по умолчанию и после значка листает сам.
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

b = Browser(1280, 720)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1280, height=720,
           deviceScaleFactor=1, mobile=False)
    b.navigate(BASE + '?preload=0')
    time.sleep(1.2)
    check('титул показан', b.js("document.getElementById('title').classList.contains('show')"))
    check('авто включено по умолчанию',
          b.js("document.getElementById('t-auto').classList.contains('on')"))
    check('значок ещё не идёт', b.js("document.getElementById('vlayer').hidden") is True)

    # 1) нажать «Авто» в меню (сначала выключаем, потом включаем — оба состояния)
    b.js("document.getElementById('t-auto').click()")
    time.sleep(0.3)
    b.js("document.getElementById('t-auto').click()")
    time.sleep(1.2)
    st = b.js("[document.getElementById('title').classList.contains('show'),"
              " document.getElementById('vlayer').hidden, __DBG.pos, __DBG.node,"
              " document.getElementById('hud').classList.contains('on')]")
    check('после «Авто» титул на месте', st[0] is True, st)
    check('после «Авто» значок НЕ пропущен', st[1] is True, st)
    check('после «Авто» позиция не сдвинулась', st[2] == 0, 'pos=%s' % st[2])
    check('после «Авто» сцена не открылась', st[3] in (None, -1), 'node=%s' % st[3])

    # 2) «Начать» → сначала значок-видео
    b.js("document.getElementById('start').click()")
    time.sleep(1.2)
    check('после «Начать» идёт значок-видео',
          b.js("document.getElementById('vlayer').hidden") is False)
    check('титул скрыт', b.js("document.getElementById('title').classList.contains('show')") is False)

    # 3) пропустить значок → страница 0 и авто-листание
    b.js("document.getElementById('vskip').click()")
    time.sleep(0.6)
    check('после значка страница 0', b.js('__DBG.pos') == 0, b.js('__DBG.pos'))
    moved = None
    t0 = time.time()
    while time.time() - t0 < 20:
        p = b.js('__DBG.pos')
        if p is not None and p >= 1:
            moved = time.time() - t0
            break
        time.sleep(0.4)
    check('авто-режим сам листает после значка', moved is not None,
          '%.1f с' % moved if moved else 'не сдвинулся')

    check('js-ошибок нет', not b.errors(), b.errors())
finally:
    b.close()

print('\nИТОГ: ' + ('ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(0 if ok else 1)
