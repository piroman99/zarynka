# -*- coding: utf-8 -*-
"""Кривая громкости музыки на длинном переходе: приглушение и возврат."""
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

b = Browser(1280, 720)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1280, height=720,
           deviceScaleFactor=1, mobile=False)
    b.navigate(BASE + '?node=%d&preload=0' % NODE['s7'])
    time.sleep(1.5)
    print('до перехода: vol=%.2f paused=%s' % (
        b.js("document.getElementById('music').volume"),
        b.js("document.getElementById('music').paused")))
    for _ in range(6):
        b.js("document.getElementById('stage').click()")
        time.sleep(0.25)
        if b.js("document.getElementById('trans').classList.contains('on')"):
            break
    t0 = time.time()
    while time.time() - t0 < 4.0:
        print('%.2f  trans=%s  logo=%s  vol=%.2f'
              % (time.time() - t0,
                 b.js("document.getElementById('trans').classList.contains('on')"),
                 b.js("document.getElementById('translogo').classList.contains('on')"),
                 b.js("document.getElementById('music').volume")))
        time.sleep(0.2)
finally:
    b.close()
