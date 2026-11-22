# -*- coding: utf-8 -*-
"""Поднять локальный http-сервер для ручной проверки Иваном и убедиться,
что страница и аудио реально отдаются. Сервер живёт до перезапуска песочницы."""
import os
import sys
import time
import threading
import functools
import http.server
import socketserver
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get('VN2_PORT', '8899'))


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        # без кеша: правим css/js — Иван сразу видит новую версию
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


srv = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), functools.partial(H, directory=ROOT))
srv.daemon_threads = True
srv.handle_error = lambda *a: None
print('serving %s on 127.0.0.1:%d' % (ROOT, PORT), flush=True)
srv.serve_forever()
