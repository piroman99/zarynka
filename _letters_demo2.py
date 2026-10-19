# -*- coding: utf-8 -*-
"""Снимки демо-страницы букв: три момента печати → вертикальная полоса."""
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
    b.navigate("http://127.0.0.1:%d/assets/pilot/letters_demo.html" % port, wait=0.5)
    for i in range(4):
        p = os.path.join(HERE, "assets", "pilot", "_d%d.png" % i)
        n = b.js("document.querySelectorAll('#text .ch').length")
        op = b.js("(function(){var a=document.querySelectorAll('#text .ch');"
                  " if(!a.length) return 'none';"
                  " return getComputedStyle(a[a.length-1]).opacity;})()")
        b.shot(p)
        shots.append(p)
        print("кадр %d: букв %s, opacity последней %s" % (i, n, op), flush=True)
        time.sleep(0.75)
    print("js-ошибки:", b.errors()[:3])
finally:
    b.close()
    srv.shutdown()

crops = []
for p in shots:
    im = Image.open(p).convert("RGB")
    crops.append(im.crop((0, int(im.height * 0.68), im.width, im.height)))
w, h = crops[0].width, crops[0].height
pad = 8
sheet = Image.new("RGB", (w, (h + pad) * len(crops) - pad), (18, 18, 20))
y = 0
for c in crops:
    sheet.paste(c, (0, y))
    y += h + pad
out = os.path.join(HERE, "assets", "pilot", "letters.png")
sheet.save(out)
print(out, sheet.size)
for p in shots:
    os.remove(p)
