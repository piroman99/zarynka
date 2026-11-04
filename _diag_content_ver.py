# -*- coding: utf-8 -*-
"""Что реально видит браузер: версия content.js, страницы 47..51 приёмной."""
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

Q = """
(function(){
  var rec=null; VN.nodes.forEach(function(n){ if(n.id==='reception') rec=n; });
  var out={total:rec.pages.length, sw:!!navigator.serviceWorker.controller, rows:[]};
  for(var i=47;i<=51;i++){ var p=rec.pages[i]; out.rows.push(i+':'+(p.bg||'-')+':'+p.tx.slice(0,40)); }
  out.pos='n/a';
  return out;
})()
"""

b = Browser(1280, 720)
try:
    b.navigate(BASE + '?instant=1&text=1&voice=0&music=0&node=11&page=49', wait=2.0)
    time.sleep(0.3)
    g = b.js(Q)
    print('страниц в приёмной:', g['total'], ' sw-контроллер:', g['sw'])
    for r in g['rows']:
        print('  ', r)
    print('pos=', g['pos'])
finally:
    b.close()
    srv.shutdown()
