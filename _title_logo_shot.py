# -*- coding: utf-8 -*-
"""Титул VN: как реально выглядит логотип на тёмном фоне (квадрат белый?)."""
import os, sys, time, threading, functools, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser
from PIL import Image

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900, deviceScaleFactor=1, mobile=False)
    b.navigate('http://127.0.0.1:%d/vn2/index.html?preload=0' % port)
    time.sleep(1.6)
    p = os.path.join(HERE, '.tmp_avmcheck', 'vn2_title.png')
    b.shot(p)
    im = Image.open(p).convert('RGB')
    # углы вокруг логотипа (лого по центру сверху)
    w, h = im.size
    print('shot', im.size)
    crop = im.crop((w // 2 - 260, 60, w // 2 + 260, 330))
    crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
    o = os.path.join(HERE, 'assets', 'review', 'review_105_title_logo.png')
    crop.save(o)
    print('saved', os.path.relpath(o, HERE))
    print('пиксель в углу кадра лого:', im.getpixel((w // 2 - 200, 100)),
          ' рядом с лого:', im.getpixel((w // 2 - 160, 120)))
finally:
    try:
        b.close()
    except Exception:
        pass
    srv.shutdown()
