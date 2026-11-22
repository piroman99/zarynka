# -*- coding: utf-8 -*-
import os, sys, time, threading, functools, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from _cdp import Browser

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

b = Browser(1600, 900)
try:
    b.navigate(BASE)
    b.wait_js("!!window.__DBG", 30)
    time.sleep(1)
    print("title attr:", b.js("document.getElementById('t-toc').getAttribute('style')"))
    b.js("document.getElementById('start').click()")
    b.wait_js("__DBG.started", 30)
    time.sleep(1.5)
    print("in-game attr:", b.js("document.getElementById('t-toc').getAttribute('style')"))
    print("in-game computed:", b.js("getComputedStyle(document.getElementById('t-toc')).display"))
    print("tools class:", b.js("document.getElementById('tools').className"))
    print("hud class:", b.js("document.getElementById('hud').className"))
    print("showHud src:", b.js("showHud ? 'global' : 'no'"))
    b.js("showHud(true)")
    time.sleep(0.2)
    print("after manual showHud(true):", b.js("document.getElementById('t-toc').getAttribute('style')"),
          b.js("getComputedStyle(document.getElementById('t-toc')).display"))
    print("errors:", b.errors()[:3])
finally:
    b.close()
    srv.shutdown()
