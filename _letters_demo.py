# -*- coding: utf-8 -*-
"""Доказательство анимации букв: снимки подряд во время печати ОДНОЙ страницы.
Показывает, что буквы входят постепенно (размытие + сдвиг), а не появляются разом."""
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
    b.navigate("http://127.0.0.1:%d/vn2/index.html?preload=0&music=0" % port, wait=1.2)
    b.js("document.getElementById('start').click()")
    time.sleep(0.5)
    b.js("document.getElementById('vskip').click()")
    time.sleep(0.6)
    # первый клик дописывает текущую страницу, второй — переходит и начинает печатать заново
    b.js("document.getElementById('next').click()")
    time.sleep(0.2)
    b.js("document.getElementById('next').click()")

    for i in range(5):
        p = os.path.join(HERE, "assets", "pilot", "_lt%d.png" % i)
        n = b.js("document.querySelectorAll('#text .ch').length")
        b.shot(p)
        shots.append(p)
        print("кадр", i, "букв:", n, flush=True)
        time.sleep(0.10)
    print("js-ошибки:", b.errors()[:3])
finally:
    b.close()
    srv.shutdown()

crops = []
for p in shots:
    im = Image.open(p).convert("RGB")
    crops.append(im.crop((0, int(im.height * 0.64), im.width, im.height)))
w, h = crops[0].width, crops[0].height
pad = 8
sheet = Image.new("RGB", (w, (h + pad) * len(crops) - pad), (18, 18, 20))
y = 0
for c in crops:
    sheet.paste(c, (0, y))
    y += h + pad
sheet = sheet.resize((w // 2, sheet.height // 2), Image.LANCZOS)
out = os.path.join(HERE, "assets", "pilot", "letters.png")
sheet.save(out)
print(out, sheet.size)
for p in shots:
    os.remove(p)
