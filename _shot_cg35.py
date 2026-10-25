# -*- coding: utf-8 -*-
"""Кадры-проверки для CG-диапазонов: стр. 22-23 (P4 v2), стр. 48-50 (сникшая Екатерина)."""
import os, sys, time, threading, functools, http.server, socketserver
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

OUT = os.path.join(HERE, '_sat')
os.makedirs(OUT, exist_ok=True)


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

GEO = """
(function(){
  var st=document.getElementById('stage').getBoundingClientRect();
  var bg=[].map.call(document.querySelectorAll('.bg.on'),
        function(e){return (getComputedStyle(e).backgroundImage||'').split('/').pop().replace(/["')]/g,'');});
  var sp=[].filter.call(document.querySelectorAll('.sprite'),function(e){return getComputedStyle(e).opacity!=='0';}).length;
  return {stage:{x:Math.round(st.x),y:Math.round(st.y),w:Math.round(st.width),h:Math.round(st.height)},
          tx:document.getElementById('text').textContent.trim(), bg:bg, sprites:sp};
})()
"""

SHOTS = [('cg35_1', 'node=11&page=22'), ('cg35_2', 'node=11&page=23'),
         ('cg48', 'node=11&page=48'), ('cg50', 'node=11&page=50'),
         ('cg51', 'node=11&page=51'), ('kate_no', 'node=11&page=3'),
         ('kate_yes', 'node=11&page=4')]

b = Browser(1920, 1080)
try:
    for name, q in SHOTS:
        url = BASE + '?instant=1&auto=0&text=1&voice=0&music=0&' + q
        b.navigate(url, wait=2.0)
        time.sleep(0.4)
        g = b.js(GEO)
        raw = os.path.join(OUT, '_raw.png')
        b.shot(raw)
        im = Image.open(raw).convert('RGB')
        st = g['stage']
        im = im.crop((st['x'], st['y'], st['x'] + st['w'], st['y'] + st['h']))
        im.save(os.path.join(OUT, 'cg_%s.png' % name))
        print('%-8s bg=%-18s sprites=%d  %s' % (name, ','.join(g['bg']), g['sprites'], g['tx'][:50]))
finally:
    b.close()
    srv.shutdown()
print('OUT', OUT)
