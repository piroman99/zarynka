# -*- coding: utf-8 -*-
"""Значок перехода на узком/портретном экране: не обрезан, по центру, без квадрата."""
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
SHOT = os.path.join(HERE, 'assets', 'review')

b = Browser(430, 932)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=430, height=932,
           deviceScaleFactor=1, mobile=True)
    b.navigate(BASE + '?node=%d&preload=0' % NODE['s7'])
    time.sleep(1.4)
    for _ in range(6):
        b.js("document.getElementById('stage').click()")
        time.sleep(0.25)
        if b.js("document.getElementById('trans').classList.contains('on')"):
            break
    time.sleep(1.0)                       # лого уже проявилось
    b.shot(os.path.join(SHOT, 'review_116_trans_logo_portrait.png'))
    geo = b.js("""(function(){
      var l=document.getElementById('translogo').getBoundingClientRect();
      return [Math.round(l.width), Math.round(l.height), Math.round(l.left),
              Math.round(l.top), window.innerWidth, window.innerHeight];
    })()""")
    print('лого в портрете: %dx%d, левый-верх (%d, %d), экран %dx%d'
          % tuple(geo))
    fits = geo[0] <= geo[4] and geo[1] <= geo[5] and geo[2] >= 0 and geo[3] >= 0
    print('ИТОГ: ' + ('вписано' if fits else 'НЕ ВПИСАНО'))
    print('js-ошибок:', b.errors() or 'нет')
finally:
    b.close()
