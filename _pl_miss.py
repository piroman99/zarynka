# -*- coding: utf-8 -*-
"""Что именно не докачалось при предзагрузке (?preload по умолчанию)."""
import os, sys, time, json, threading, functools, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _cdp


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/vn2/index.html' % port
b = _cdp.Browser(1440, 900)
try:
    b.navigate(URL + '?instant=1&voice=0&music=0', wait=0.2)
    for i in range(60):
        st = b.js("({miss:[...__PL.miss], img:__PL.img.size, aud:__PL.aud.size, vid:__PL.vid.size, q:__PL.queue()})")
        if st['q'] == 0 and i > 3:
            break
        time.sleep(0.5)
    print(json.dumps(st, ensure_ascii=False, indent=1))
    print('errors:', [e for e in b.errors() if 'manifest' not in e][:5])
finally:
    b.close()
    srv.server_close()
