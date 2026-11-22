# -*- coding: utf-8 -*-
"""Геометрия панели перехода: влезает ли в экран и не режется ли поле.

Проверяем два размера: 1440x900 (ноутбук) и 420x760 (телефон, портрет).
Панель не должна выходить за экран, поле ввода должно быть не уже 100 px,
кнопка «Перейти» — не меньше 60 px, шрифт в поле — не меньше 16 px
(иначе iOS зумит страницу при фокусе).
"""
import functools
import http.server
import os
import socketserver
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402

GEO = """(function(){
  var card=document.querySelector('.jump-inner'), inp=document.getElementById('jump-in'),
      go=document.getElementById('jump-go'), hint=document.getElementById('jump-hint');
  function r(e){var b=e.getBoundingClientRect();
    return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};}
  return {vw:innerWidth, vh:innerHeight, card:r(card), inp:r(inp), go:r(go), hint:r(hint),
          fs:parseFloat(getComputedStyle(inp).fontSize),
          z:getComputedStyle(document.getElementById('jump')).zIndex};
})()"""


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(H, directory=ROOT))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

fails = []


def check(name, cond, extra=''):
    print('%-46s %s %s' % (name, 'OK' if cond else '!!! ПРОВАЛ', extra))
    if not cond:
        fails.append(name)


for w, h in ((1440, 900), (390, 844), (360, 640)):
    print('--- %dx%d ---' % (w, h))
    b = Browser(w, h)
    try:
        # честная мобильная вьюпорт: без этого headless отдаёт свой минимум по ширине
        b.send('Emulation.setDeviceMetricsOverride', width=w, height=h,
               deviceScaleFactor=1, mobile=(w < 600))
        b.navigate(BASE + '?instant=1&auto=0&voice=0&music=0', wait=2.2)
        b.js("window.__TOC && null;")
        # открываем панель тем же путём, что пользователь: пять тапов по логотипу
        b.js("""(function(){var l=document.querySelector('#title .logo');
          for(var i=0;i<5;i++) l.dispatchEvent(new MouseEvent('click',{bubbles:true}));})()""")
        g = b.js(GEO)
        card, inp, go = g['card'], g['inp'], g['go']
        check('панель открыта', b.js("document.getElementById('jump').classList.contains('show')"))
        check('карточка внутри экрана по ширине', card['x'] >= 0 and card['x'] + card['w'] <= g['vw'],
              'x=%d w=%d vw=%d' % (card['x'], card['w'], g['vw']))
        check('карточка внутри экрана по высоте', card['y'] >= 0 and card['y'] + card['h'] <= g['vh'],
              'y=%d h=%d vh=%d' % (card['y'], card['h'], g['vh']))
        check('поле ввода не уже 100 px', inp['w'] >= 100, 'w=%d' % inp['w'])
        check('кнопка «Перейти» не уже 60 px', go['w'] >= 60, 'w=%d' % go['w'])
        check('шрифт поля >= 16 px (iOS не зумит)', g['fs'] >= 16, '%.1f px' % g['fs'])
        check('панель выше оглавления (z-index)', int(g['z']) > 24, 'z=%s' % g['z'])
        check('поле и кнопка на одной строке',
              abs(inp['y'] - go['y']) <= 2, 'inp.y=%d go.y=%d' % (inp['y'], go['y']))
        check('подсказка под полем', g['hint']['y'] > inp['y'] + inp['h'],
              'hint.y=%d inp.bottom=%d' % (g['hint']['y'], inp['y'] + inp['h']))
        check('нет ошибок JS', not b.errors(), '; '.join(b.errors()[:2]))
        b.shot(os.path.join(ROOT, '_sat', 'jump_%dx%d.png' % (w, h)))
    finally:
        b.close()

srv.shutdown()
print('\nпровалов: %d %s' % (len(fails), fails if fails else ''))
sys.exit(0 if not fails else 1)
