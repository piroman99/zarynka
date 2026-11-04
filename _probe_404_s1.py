# -*- coding: utf-8 -*-
"""Какой ресурс отдаёт 404 на страницах пролога (URL, а не только текст ошибки).

    python3 _probe_404_s1.py

Открывает vn2 на локальном http-сервере, идёт по всем страницам пролога
(клики «дальше» в INSTANT), собирает Log.entryAdded с URL и печатает те, где
level=error и status 404.
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
    b.navigate(BASE + '?instant=1&auto=0&voice=0&music=0&node=3&page=0', wait=2.5)
    # пройти весь пролог и приёмную — 90 кликов с запасом
    for _ in range(40):
        b.js("(function(){var n=document.getElementById('next');if(n)n.click();return 1})()")
        time.sleep(0.12)
    time.sleep(1.0)
    bad = []
    for m in b.logs:
        if m.get('method') != 'Log.entryAdded':
            continue
        e = m['params']['entry']
        if e.get('level') != 'error':
            continue
        url = e.get('url') or ''
        net = (e.get('networkRequestId') or '')
        bad.append((str(e.get('text'))[:90], url[:140], net))
    print('ошибок уровня error: %d' % len(bad))
    for t, u, n in bad[:20]:
        print('  %s\n    url=%s net=%s' % (t, u or '(нет url)', n or '-'))
finally:
    b.close()
    srv.shutdown()
