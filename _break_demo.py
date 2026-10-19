# -*- coding: utf-8 -*-
"""Снимки перебивки: последняя страница пролога → клик → кабинет Старика.
Доказывает, что стык сцен закрыт акварельной заливкой (а не рывком)."""
import os, sys, time, threading, functools, http.server, socketserver
from PIL import Image

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
shots = []
try:
    # node 8 = s7 (последний кадр пролога)
    b.navigate("http://127.0.0.1:%d/vn2/index.html?node=8&page=0&music=0" % port, wait=1.4)
    p = os.path.join(HERE, "assets", "pilot", "_sb0.png")
    b.shot(p); shots.append(("до клика: пролог", p))
    b.js("document.getElementById('next').click()")   # дописать страницу
    time.sleep(0.3)
    b.js("document.getElementById('next').click()")   # перейти к следующей сцене
    for i, wait in enumerate((0.05, 0.07, 0.10, 0.90)):
        time.sleep(wait)
        p = os.path.join(HERE, "assets", "pilot", "_sb%d.png" % (i + 1))
        n = b.js("document.querySelectorAll('#brk.on').length")
        node = b.js("window.__DBG.node")
        txt = b.js("document.getElementById('text').textContent.slice(0,40)")
        b.shot(p)
        shots.append(("brk.on=%s node=%s | %s" % (n, node, txt[:34]), p))
    print("errs:", b.errors()[:3])
finally:
    b.close()
    srv.shutdown()

tiles = []
for cap, p in shots:
    im = Image.open(p).convert("RGB")
    tiles.append((cap, im.resize((im.width // 2, im.height // 2), Image.LANCZOS)))
    print(cap)

w, h = tiles[0][1].size
pad = 8
sheet = Image.new("RGB", (w * 2 + pad, (h + pad) * 3), (18, 18, 20))
for i, (cap, im) in enumerate(tiles):
    sheet.paste(im, ((i % 2) * (w + pad), (i // 2) * (h + pad)))
out = os.path.join(HERE, "assets", "pilot", "scene_break.png")
sheet.save(out)
print(out, sheet.size)
for _, p in shots:
    os.remove(p)
