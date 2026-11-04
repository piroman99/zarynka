# -*- coding: utf-8 -*-
"""Скриншоты кадра s1 (обе страницы: стена → подворотня) и кадра p6 (лунная станция).

    python3 _shot_s1_p6.py

Пишет в `_sat/`:
  s1_p0_wall.png   — стр. 1 кадра s1 (стена с граффити, bg = img/prolog/s1a.webp)
  s1_p1_alley.png  — стр. 2 кадра s1 (подворотня, bg = img/prolog/s1.webp)
  p6_p0.png / p6_p1.png — обе страницы кадра p6
Печатает фактический фон каждой страницы — проверка, что кадр подменился.
"""
import os
import sys
import time
import threading
import functools
import http.server
import socketserver
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
  return {stage:{x:Math.round(st.x),y:Math.round(st.y),w:Math.round(st.width),h:Math.round(st.height)},
          tx:document.getElementById('text').textContent.trim(), bg:bg};
})()
"""

SHOTS = [('s1_p0_wall', 'node=3&page=0'),
         ('s1_p1_alley', 'node=3&page=1'),
         ('p6_p0', 'node=4&page=0'),
         ('p6_p1', 'node=4&page=1')]

b = Browser(1920, 1080)
try:
    for name, q in SHOTS:
        url = BASE + '?instant=1&auto=0&text=1&voice=0&music=0&' + q
        b.navigate(url, wait=2.0)
        time.sleep(0.4)
        g = b.js(GEO)
        raw = os.path.join(OUT, '_raw_s1p6.png')
        b.shot(raw)
        im = Image.open(raw).convert('RGB')
        st = g['stage']
        im = im.crop((st['x'], st['y'], st['x'] + st['w'], st['y'] + st['h']))
        im.save(os.path.join(OUT, name + '.png'))
        print('%-12s bg=%-24s %s' % (name, ','.join(g['bg']), g['tx'][:72]))
finally:
    b.close()
    srv.shutdown()
print('OUT', OUT)
