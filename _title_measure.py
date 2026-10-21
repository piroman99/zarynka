# -*- coding: utf-8 -*-
"""Замер геометрии стартового экрана: где логотип, «Начать», полоска, «Тизер».
Сравниваем «без титров» (по умолчанию) и «с титрами» (?titles=1), в 16:9 и в портрете."""
import os
import sys
import time
import json
import threading
import functools
import http.server
import socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

BOX = """
(function(){
  function r(sel){var e=document.querySelector(sel); if(!e) return null;
    var b=e.getBoundingClientRect(), cs=getComputedStyle(e);
    return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height),
            cx:Math.round(b.x+b.width/2),cy:Math.round(b.y+b.height/2),d:cs.display};}
  return {vw:innerWidth,vh:innerHeight,inner:r('.title-inner'),logo:r('.logo'),
          start:r('#start'),pl:r('#pl'),teaser:r('#teaser'),tt:r('#tt'),
          cls:document.body.className};
})()
"""


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

for vw, vh, tag in ((1280, 720, '16x9'), (390, 844, 'portrait')):
    b = Browser(vw, vh)
    try:
        b.send('Emulation.setDeviceMetricsOverride', width=vw, height=vh,
               deviceScaleFactor=1, mobile=False)
        for q, name in (('?preload=0', 'notitles'), ('?preload=0&titles=1', 'titles')):
            b.navigate(BASE + q)
            time.sleep(1.0)
            box = b.js(BOX)
            print('== %s / %s' % (tag, name))
            print(json.dumps(box, ensure_ascii=False, indent=1))
            b.shot(os.path.join(HERE, '_tmp_title_%s_%s.png' % (tag, name)))
    finally:
        b.close()
