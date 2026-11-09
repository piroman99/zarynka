# -*- coding: utf-8 -*-
"""Геометрия сворачиваемого тулбара в портрете: не вылезает ли ряд за экран.

Проверяем 4 популярных портретных размера: свёрнуто (☰ [+⏸]) и раскрыто
(все 6 кнопок) — левый край >= 0, правый <= ширины, ряд не залезает в
подстрочник (#box начинается с 56.25vw).
"""
import os
import sys
import time
import threading
import functools
import http.server
import socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

ok = True
RECTS = """(function(){
  var ids=['t-auto','t-pause','t-text','t-voice','t-music','t-full','t-menu'];
  var out={tools:document.getElementById('tools').getBoundingClientRect().toJSON(),
           box:document.getElementById('box').getBoundingClientRect().toJSON(),
           w:innerWidth, h:innerHeight, open:document.getElementById('tools').classList.contains('open'), b:{}};
  ids.forEach(function(i){var e=document.getElementById(i);
    if(e && getComputedStyle(e).display!=='none'){
      var r=e.getBoundingClientRect(); out.b[i]=[Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom)];
    }});
  return out;})()"""


def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK   ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

SIZES = [(320, 568), (360, 740), (390, 844), (412, 915)]
b = Browser(390, 844)
try:
    for (w, h) in SIZES:
        b.send('Emulation.setDeviceMetricsOverride', width=w, height=h,
               deviceScaleFactor=2, mobile=True)
        b.navigate(BASE + '?preload=0&auto=0')
        time.sleep(1.2)
        c = b.js(RECTS)
        vis = sorted(c['b'])
        check('%dx%d свёрнуто: только ☰ (авто выкл)' % (w, h), vis == ['t-menu'], vis)
        r = c['b'].get('t-menu', [0, 0, 0, 0])
        check('%dx%d свёрнуто: ☰ в пределах экрана' % (w, h), r[0] >= 0 and r[2] <= w, r)
        b.js("document.getElementById('t-menu').click()")
        time.sleep(0.3)
        o = b.js(RECTS)
        vis = sorted(o['b'])
        check('%dx%d раскрыто: все 6 кнопок' % (w, h),
              vis == ['t-auto', 't-full', 't-menu', 't-music', 't-text', 't-voice'], vis)
        t = o['tools']
        check('%dx%d раскрыто: ряд в пределах экрана' % (w, h),
              t['left'] >= 0 and t['right'] <= w, [round(t['left']), round(t['right'])])
        bottom = max(v[3] for v in o['b'].values())
        box_top = o['box']['top']
        check('%dx%d раскрыто: ряд не залезает в подстрочник' % (w, h),
              bottom <= box_top, 'низ ряда %d, верх #box %d' % (bottom, round(box_top)))
        print('        %dx%d: ряд %d..%d px, ширина %d, высота %d'
              % (w, h, round(t['left']), round(t['right']), round(t['width']), round(t['height'])))
finally:
    b.close()

print('\nИТОГ: ' + ('ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(0 if ok else 1)
