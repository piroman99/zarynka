# -*- coding: utf-8 -*-
import os, sys, time, threading, functools, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]
b = Browser(1600, 900)
try:
    for node, page in ((9, 0), (9, 3), (10, 0), (10, 7), (10, 33)):
        b.navigate("http://127.0.0.1:%d/vn2/index.html?node=%d&page=%d" % (port, node, page), wait=1.2)
        d = b.js("""JSON.stringify({
            pos: window.__DBG.pos, node: window.__DBG.node,
            txt: document.getElementById('text').textContent.slice(0, 50),
            bg: getComputedStyle(document.getElementById('bg-a')).backgroundImage.slice(-30),
            bg2: getComputedStyle(document.getElementById('bg-b')).backgroundImage.slice(-30),
            who: document.getElementById('name').textContent,
        })""")
        print(node, page, d, flush=True)
finally:
    b.close()
    srv.shutdown()
