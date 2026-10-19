# -*- coding: utf-8 -*-
"""По одному кадру на файл: кабинет Старика и приёмная (акварель).
Перед снимком проверяем __DBG.pos/текст — иначе снимок может опередить рендер."""
import os, sys, time, threading, functools, http.server, socketserver

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

SHOTS = [(9, 0, "scene_cabinet"), (10, 7, "scene_kate_enter"), (10, 33, "scene_kate_ask")]
b = Browser(1600, 900)
try:
    for node, page, name in SHOTS:
        url = "http://127.0.0.1:%d/vn2/index.html?node=%d&page=%d&music=0" % (port, node, page)
        b.navigate(url, wait=1.0)
        for _ in range(40):
            st = b.js("JSON.stringify({p:window.__DBG.pos,n:window.__DBG.node,"
                      "t:document.getElementById('text').textContent.length})")
            if st and '"p"' in st:
                break
            time.sleep(0.2)
        time.sleep(1.2)   # дать фоновой картинке декодироваться
        out = os.path.join(HERE, "assets", "pilot", name + ".png")
        b.shot(out)
        print(name, st, flush=True)
    print("errs:", b.errors()[:3])
finally:
    b.close()
    srv.shutdown()
