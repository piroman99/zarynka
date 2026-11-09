# -*- coding: utf-8 -*-
"""Геометрия титула с третьей кнопкой «Оглавление»: не вылезает ли блок
за вьюпорт и не наезжают ли кнопки друг на друга.

Экраны: 1600x900 (десктоп), 390x844 (портрет), 360x740, 412x915,
         844x390 (телефон альбом), 740x360 (короткий).
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
SCREENS = [(1600, 900, False), (390, 844, True), (360, 740, True),
           (412, 915, True), (844, 390, True), (740, 360, True)]


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

GEO = """(function(){
  var ids=['start','toc-open','teaser'];
  var r={};
  ids.forEach(function(id){var e=document.getElementById(id);
    var b=e.getBoundingClientRect();
    r[id]={t:Math.round(b.top),b:Math.round(b.bottom),l:Math.round(b.left),
           r:Math.round(b.right),w:Math.round(b.width),h:Math.round(b.height),
           vis:getComputedStyle(e).display!=='none'};});
  var ti=document.querySelector('.title-inner').getBoundingClientRect();
  r.inner={t:Math.round(ti.top),b:Math.round(ti.bottom)};
  r.vw=innerWidth; r.vh=innerHeight;
  return r;})()"""

b = Browser(1600, 900)
try:
    for w, h, mob in SCREENS:
        b.send('Emulation.setDeviceMetricsOverride', width=w, height=h,
               deviceScaleFactor=1, mobile=mob)
        if mob:
            b.send('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=5)
        b.navigate(BASE + '?preload=0')
        time.sleep(1.2)
        g = b.js(GEO)
        tag = '%dx%d' % (w, h)
        print('  --', tag, 'start', g['start'], 'toc', g['toc-open'], 'inner', g['inner'])
        check(tag + ': «Начать» и «Оглавление» в одном ряду',
              abs(g['start']['t'] - g['toc-open']['t']) < 30 and g['toc-open']['l'] >= g['start']['r'] - 1,
              'start.l=%d start.r=%d toc.l=%d' % (g['start']['l'], g['start']['r'], g['toc-open']['l']))
        check(tag + ': все три кнопки видимы',
              g['start']['vis'] and g['toc-open']['vis'] and g['teaser']['vis'])
        check(tag + ': «Оглавление» внутри экрана по ширине',
              g['toc-open']['l'] >= 0 and g['toc-open']['r'] <= g['vw'] + 0.5,
              '%d..%d / %d' % (g['toc-open']['l'], g['toc-open']['r'], g['vw']))
        check(tag + ': блок титула влезает по высоте',
              g['inner']['t'] >= -0.5 and g['inner']['b'] <= g['vh'] + 0.5,
              '%d..%d / %d' % (g['inner']['t'], g['inner']['b'], g['vh']))
        check(tag + ': кнопки не перекрываются',
              b.js("(function(){var a=['start','toc-open','teaser'].map(function(i){"
                   "return document.getElementById(i).getBoundingClientRect()});"
                   "function ov(p,q){return Math.min(p.right,q.right)>Math.max(p.left,q.left)"
                   "&& Math.min(p.bottom,q.bottom)>Math.max(p.top,q.top)}"
                   "return !(ov(a[0],a[1])||ov(a[0],a[2])||ov(a[1],a[2]))})()") is True,
              'start %d..%d / toc %d..%d' % (g['start']['b'], g['start']['t'],
                                             g['toc-open']['b'], g['toc-open']['t']))
    errs = b.errors()
    check('js-ошибок нет', not errs, errs[:2])
finally:
    b.close()
    srv.shutdown()

print('\nИТОГ:', 'ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОВАЛЫ')
sys.exit(0 if ok else 1)
