# -*- coding: utf-8 -*-
"""Какая страница открывается по ?node=11&page=N (проверка смещения)."""
import os, sys, time, threading, functools, http.server, socketserver
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

G = """
(function(){
  var bg=[].map.call(document.querySelectorAll('.bg.on'),
        function(e){return (getComputedStyle(e).backgroundImage||'').split('/').pop().replace(/["')]/g,'');});
  return {bg:bg[0]||'-', tx:document.getElementById('text').textContent.trim().slice(0,46)};
})()
"""

b = Browser(1280, 720)
try:
    for n in list(range(19, 25)) + list(range(46, 53)):
        b.navigate(BASE + '?instant=1&text=1&voice=0&music=0&node=11&page=%d' % n, wait=1.2)
        time.sleep(0.2)
        g = b.js(G)
        print('page=%-3d bg=%-16s %s' % (n, g['bg'], g['tx']))
finally:
    b.close()
    srv.shutdown()
