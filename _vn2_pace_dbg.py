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

b = Browser(1280, 720)
try:
    b.navigate("http://127.0.0.1:%d/vn2/index.html?auto=1&music=0" % port, wait=1.5)
    def st(tag):
        v = b.js("""() => ({
            pos: window.__DBG ? window.__DBG.pos : 'noDBG',
            title: document.getElementById('title').classList.contains('show'),
            vlayer: !document.getElementById('vlayer').hidden,
            hud: document.getElementById('hud').classList.contains('on'),
            text: (document.getElementById('text')||{}).textContent.slice(0,40),
            auto: document.getElementById('t-auto').className,
        })""")
        print(tag, v, flush=True)
    st("load:")
    print("click start:", b.js("() => { const s=document.getElementById('start'); if(!s) return 'no'; s.click(); return 'ok'; }"))
    time.sleep(1.0); st("after start:")
    print("click vskip:", b.js("() => { const s=document.getElementById('vskip'); if(!s) return 'no'; s.click(); return 'ok'; }"))
    time.sleep(1.0); st("after skip:")
    for i in range(6):
        time.sleep(2.0)
        st("t+%ds:" % ((i + 1) * 2))
    print("errors:", b.errors()[:5])
finally:
    b.close()
    srv.shutdown()
