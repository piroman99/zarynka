# -*- coding: utf-8 -*-
"""Одна навигация: какой индекс приёмной реально показан при ?page=N."""
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
  var shown=document.getElementById('text').textContent.trim();
  var idx=-1;
  for(var i=0;i<rec.pages.length;i++){
    if(rec.pages[i].tx.trim()===shown){ idx=i; break; }
  }
  var bg=[].map.call(document.querySelectorAll('.bg.on'),
        function(e){return (getComputedStyle(e).backgroundImage||'').split('/').pop().replace(/["')]/g,'');});
  return {idx:idx, bg:bg, tx:shown.slice(0,44)};
})()
"""

b = Browser(1280, 720)
try:
    for n in (20, 21, 22, 23, 47, 48, 49, 50, 51):
        b.navigate(BASE + '?instant=1&text=1&voice=0&music=0&node=11&page=%d' % n, wait=1.6)
        time.sleep(0.25)
        g = b.js(Q)
        print('page=%-3d -> индекс %-3s bg=%-24s %s' % (n, g['idx'], ','.join(g['bg']), g['tx']))
finally:
    b.close()
    srv.shutdown()
