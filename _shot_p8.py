# -*- coding: utf-8 -*-
"""Скриншоты кадра p8 (гидролаборатория) в движке: сам кадр + соседи (p7, s3)."""
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
from _vn2_nodes import node_index

OUT = os.path.join(HERE, "_sat")
os.makedirs(OUT, exist_ok=True)

IDX = {n: node_index(n) for n in ("p7", "p8", "s3")}
print("индексы узлов:", IDX)


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:%d/vn2/index.html" % PORT

GEO = """
(function(){
  var st=document.getElementById('stage').getBoundingClientRect();
  var bg=[].map.call(document.querySelectorAll('.bg.on'),
        function(e){return (getComputedStyle(e).backgroundImage||'').split('/').pop().replace(/["')]/g,'');});
  return {stage:{x:Math.round(st.x),y:Math.round(st.y),w:Math.round(st.width),h:Math.round(st.height)},
          tx:document.getElementById('text').textContent.trim(), bg:bg};
})()
"""

SHOTS = [("p7_last", "node=%d&page=0" % IDX["p7"]),
         ("p8_p0", "node=%d&page=0" % IDX["p8"]),
         ("s3_p0", "node=%d&page=0" % IDX["s3"])]

b = Browser(1920, 1080)
try:
    for name, q in SHOTS:
        url = BASE + "?instant=1&auto=0&text=1&voice=0&music=0&" + q
        b.navigate(url, wait=2.0)
        time.sleep(0.4)
        g = b.js(GEO)
        raw = os.path.join(OUT, "_raw_p8.png")
        b.shot(raw)
        im = Image.open(raw).convert("RGB")
        st = g["stage"]
        im = im.crop((st["x"], st["y"], st["x"] + st["w"], st["y"] + st["h"]))
        im.save(os.path.join(OUT, "p8_%s.png" % name))
        print("%-8s bg=%-24s %s" % (name, ",".join(g["bg"]), g["tx"][:70]))
finally:
    b.close()
    srv.shutdown()
print("OUT", OUT)