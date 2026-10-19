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
    b.navigate("http://127.0.0.1:%d/assets/pilot/letters_demo.html" % port, wait=1.0)
    print("n:", b.js("document.querySelectorAll('#text .ch').length"))
    print("txt:", b.js("document.getElementById('text').textContent.slice(0,40)"))
    print("style:", b.js("getComputedStyle(document.querySelector('#text .ch') || document.body).animationName"))
    print("op:", b.js("(function(){var a=document.querySelectorAll('#text .ch'); if(!a.length) return 'none'; return getComputedStyle(a[a.length-1]).opacity;})()"))
    print("flt:", b.js("(function(){var a=document.querySelectorAll('#text .ch'); if(!a.length) return 'none'; return getComputedStyle(a[a.length-1]).filter;})()"))
    print("errs:", b.errors()[:4])
finally:
    b.close()
    srv.shutdown()
