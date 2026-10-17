# -*- coding: utf-8 -*-
"""Замер до/после WebP: сколько теперь качает браузер и за сколько идёт предзагрузка."""
import os, sys, time, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

BYTES = {'n': 0}
LOCK = threading.Lock()


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        p = os.path.join(HERE, self.path.split('?')[0].lstrip('/'))
        try:
            sz = os.path.getsize(p)
        except OSError:
            sz = 0
        with LOCK:
            BYTES['n'] += sz
        return super().do_GET()


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % port

b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900, deviceScaleFactor=1, mobile=False)
    t0 = time.time()
    b.navigate(BASE)
    done = b.wait_js("(function(){var e=document.getElementById('pl');return !!(e&&e.classList.contains('done'))})()",
                     timeout=180, every=0.2)
    dt = time.time() - t0
    with LOCK:
        total = BYTES['n']
    print('предзагрузка: %s за %.1f с' % ('завершена' if done else 'НЕ завершена', dt))
    print('кэши:', b.js("JSON.stringify({img: __PL.img.size, aud: __PL.aud.size, vid: __PL.vid.size, miss: __PL.miss.size})"))
    print('скачано с сервера ВСЕГО за этот прогон: %.2f MB' % (total / 1048576))

    # что именно лежит в img: суммарный вес
    tot_img = 0
    for root, _, fs in os.walk(os.path.join(HERE, 'vn2', 'img')):
        for f in fs:
            tot_img += os.path.getsize(os.path.join(root, f))
    print('вес vn2/img на диске: %.2f MB' % (tot_img / 1048576))
finally:
    b.close()
    srv.shutdown()
    srv.server_close()
