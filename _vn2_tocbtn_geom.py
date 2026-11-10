# -*- coding: utf-8 -*-
"""Геометрия тулбара с новой книжкой-оглавлением (Иван 2026-11-10, вариант A).

Для 5 экранов (ландшафт от 1600x900 до 740x360 и портрет 390x844):
  * кнопки ряда не вылезают за экран и не перекрывают друг друга;
  * книжка видна в ландшафте и входит в ряд в портрете;
  * ряд не наезжает на кадр больше, чем раньше (высота ряда <= 56 px).
PNG не вижу — поэтому проверка числовая.
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
JS_RECTS = """(function(){
  var out = [];
  document.querySelectorAll('#tools .tg').forEach(function(b){
    var r = b.getBoundingClientRect(), st = getComputedStyle(b);
    if (st.display === 'none' || !r.width) return;
    out.push({id: b.id, x: Math.round(r.left), y: Math.round(r.top),
              w: Math.round(r.width), h: Math.round(r.height), r: Math.round(r.right)});
  });
  return out;
})()"""


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

SCREENS = [(1600, 900), (1366, 768), (1024, 600), (740, 360), (390, 844), (360, 740), (320, 568)]


def open_page(w, h, tries=3):
    """headless Chrome изредка отдаёт мёртвый WS — поднимаем заново"""
    for i in range(tries):
        b = Browser(w, h)
        try:
            b.send('Emulation.setDeviceMetricsOverride', width=w, height=h,
                   deviceScaleFactor=1, mobile=(h > w))
            b.navigate(BASE + '?preload=0')
            if b.wait_js("!!window.__DBG", 25):
                return b
        except Exception as e:
            print('   (попытка %d не удалась: %s)' % (i + 1, type(e).__name__))
        b.close()
        time.sleep(1.5)
    raise RuntimeError('не удалось открыть страницу %dx%d' % (w, h))

for (w, h) in SCREENS:
    b = open_page(w, h)
    try:
        time.sleep(0.8)
        b.js("document.getElementById('start').click()")
        b.wait_js("document.getElementById('hud').classList.contains('on')", 40)
        time.sleep(0.8)
        vw = b.js("innerWidth")            # вьюпорт после override — как на устройстве
        vh = b.js("innerHeight")
        portrait = vh > vw
        if portrait:
            b.js("document.getElementById('t-menu').click()")
            time.sleep(0.4)
        rects = b.js(JS_RECTS) or []
        ids = [r['id'] for r in rects]
        print('  %dx%d (вьюпорт %dx%d): %s' % (w, h, vw, vh,
              ', '.join('%s@%d' % (r['id'], r['x']) for r in rects)))
        check('%dx%d: книжка в ряду' % (w, h), 't-toc' in ids, ids)
        check('%dx%d: всё в экране по ширине' % (w, h), all(r['r'] <= vw for r in rects),
              [(r['id'], r['r'], vw) for r in rects if r['r'] > vw])
        check('%dx%d: ничего не уехало за левый край' % (w, h), all(r['x'] >= 0 for r in rects),
              [(r['id'], r['x']) for r in rects if r['x'] < 0])
        # перекрытия: кнопки идут в один ряд с зазором
        srt = sorted(rects, key=lambda r: r['x'])
        ovl = [(srt[i]['id'], srt[i + 1]['id']) for i in range(len(srt) - 1)
               if srt[i]['r'] > srt[i + 1]['x'] + 1]
        check('%dx%d: кнопки не перекрываются' % (w, h), not ovl, ovl)
        check('%dx%d: ряд не выше 56 px' % (w, h), all(r['h'] <= 56 for r in rects),
              max([r['h'] for r in rects] or [0]))
        # ряд не залезает на центр кадра (кадр смотрим в средней трети)
        top = min([r['y'] for r in rects] or [0])
        check('%dx%d: ряд в верхней полосе (y < 15%% высоты)' % (w, h), top < vh * 0.15, top)
        errs = [e for e in b.errors() if 'favicon' not in e]
        check('%dx%d: ошибок нет' % (w, h), not errs, errs[:2])
    finally:
        b.close()

srv.shutdown()
print('\nИТОГ:', 'всё зелёное' if ok else 'есть провалы')
sys.exit(0 if ok else 1)
