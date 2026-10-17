# -*- coding: utf-8 -*-
"""Главная проверка: после предзагрузки листание НЕ должно вызывать НИ ОДНОГО сетевого запроса.
Плюс снимок титула с полосой загрузки и снимок страницы посреди пролога.
"""
import os, sys, time, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

REQ = []
LOCK = threading.Lock()


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        with LOCK:
            REQ.append((time.time(), self.path))
        return super().do_GET()


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % port

b = Browser(1600, 900)
try:
    b.navigate(BASE)
    # снимок титула ВО ВРЕМЯ загрузки (если успеем) — потом проверим полосу
    time.sleep(0.15)
    b.shot(os.path.join(HERE, 'assets', 'review', '_pl_title_loading.png'))
    ok = b.wait_js("(function(){var e=document.getElementById('pl');return !!(e&&e.classList.contains('done'))})()",
                   timeout=90)
    print('предзагрузка завершена:', ok)
    b.shot(os.path.join(HERE, 'assets', 'review', '_pl_title_done.png'))

    # старт и пролистывание
    b.js("document.getElementById('start').click()")
    b.wait_js("!document.getElementById('vlayer').hidden", timeout=30)
    b.js("document.getElementById('vskip').click()")
    time.sleep(0.8)

    with LOCK:
        REQ.clear()          # обнуляем лог: дальше считаем ТОЛЬКО запросы во время просмотра

    pages = []
    for i in range(24):
        pages.append(b.js("window.__DBG ? __DBG.pos : -1"))
        b.js("document.getElementById('next').click()")
        time.sleep(0.35)
        # досрочно дописать печать не нужно: next() сам досочиняет
    pages.append(b.js("__DBG.pos"))

    with LOCK:
        during = list(REQ)
    print('позиции:', pages[0], '→', pages[-1])
    print('сетевых запросов ВО ВРЕМЯ просмотра 24 страниц:', len(during))
    for t, q in during[:10]:
        print('   ', q)
    print('voice.src:', b.js("document.getElementById('voice').getAttribute('src')"))
    print('readyState voice:', b.js("document.getElementById('voice').readyState"))
    b.shot(os.path.join(HERE, 'assets', 'review', '_pl_page_after.png'))
    errs = b.errors()
    print('ошибок JS:', len(errs))
    for e in errs[:8]:
        print('  ', e)
finally:
    b.close()
    srv.shutdown()
    srv.server_close()
