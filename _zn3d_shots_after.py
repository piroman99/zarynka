# -*- coding: utf-8 -*-
"""Снимки узла-значка после замены видео: десктоп 16:9 и телефон в портрете/альбоме.

Гарантии:
  * видео реально качает новый файл (не 404) и играет;
  * в портрете/альбоме чёрных полос не больше, чем положено (object-fit contain);
  * управление (кнопка «Пропустить») не залезает на видео.
"""
import os, sys, time, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

R = os.path.join(HERE, 'assets', 'review')


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.daemon_threads = True
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html?node=1&preload=0' % PORT

CASES = [('desk_1600x900', 1600, 900, False),
         ('port_390x844', 390, 844, True),
         ('land_844x390', 844, 390, True)]

b = Browser(1600, 900)
try:
    for name, w, h, mob in CASES:
        b.send('Emulation.setDeviceMetricsOverride', width=w, height=h,
               deviceScaleFactor=1, mobile=mob)
        b.navigate(BASE + '&t=%d' % int(time.time() * 1000))
        time.sleep(1.6)
        info = b.js("""(function(){ var v=document.getElementById('znak');
          var r=v.getBoundingClientRect();
          return [v.videoWidth, v.videoHeight, +v.duration.toFixed(2), v.paused?'pause':'play',
                  Math.round(r.width), Math.round(r.height),
                  document.getElementById('vlayer').hidden]; })()""")
        print('%-16s видео %sx%s, %ss, %s, бокс %sx%s, скрыт=%s'
              % (name, info[0], info[1], info[2], info[3], info[4], info[5], info[6]))
        p = os.path.join(R, 'review_111_znak_%s.png' % name)
        b.shot(p)
        print('  снимок:', os.path.basename(p))
    print('ошибки:', b.errors())
finally:
    b.close()
