# -*- coding: utf-8 -*-
"""Сворачиваемый тулбар в ПОРТРЕТЕ (запрос Ивана 2026-11-09).

Проверяем на 390x844 (mobile=True):
  1) в портрете виден только ☰, остальные кнопки скрыты;
  2) по ☰ ряд раскрывается (display != none у всех), значок меняется на ✕;
  3) клик по тумблеру И сворачивает ряд, И переключает сам тумблер
     (ловим в фазе перехвата — кнопки зовут stopPropagation);
  4) клик по кадру мимо тулбара сворачивает ряд;
  5) в авто-режиме ⏸ остаётся снаружи и нажимается при свёрнутом ряде;
  6) на десктопе 1600x900 всё как раньше: ☰ скрыт, ряд виден.

Скриншоты: _sat/tools_m_collapsed.png, tools_m_open.png, tools_m_pause.png,
            tools_d_desktop.png
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
DISP = "(function(){var e=document.getElementById('%s');" \
       "return getComputedStyle(e).display})()"
OPEN = "document.getElementById('tools').classList.contains('open')"


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

b = Browser(390, 844)
try:
    # ---------- портрет ----------
    b.send('Emulation.setDeviceMetricsOverride', width=390, height=844,
           deviceScaleFactor=2, mobile=True)
    b.send('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=5)
    b.navigate(BASE + '?preload=0')
    time.sleep(1.5)

    check('портрет: медиазапрос сработал',
          b.js("matchMedia('(max-aspect-ratio:1/1)').matches") is True)
    check('☰ виден', b.js(DISP % 't-menu') != 'none', b.js(DISP % 't-menu'))
    for bid in ('t-auto', 't-text', 't-voice', 't-music', 't-full'):
        check('свёрнуто: %s скрыт' % bid, b.js(DISP % bid) == 'none', b.js(DISP % bid))
    check('☰ подписан как «Кнопки»',
          b.js("document.getElementById('t-menu').title") == 'Кнопки: авто, текст, голос, музыка, экран')

    # старт: пролог с кадром — скриншот поверх арта
    b.js("document.getElementById('start').click()")
    time.sleep(1.2)
    b.js("(function(){var v=document.getElementById('vskip'); if(v) v.click();})()")
    time.sleep(1.5)
    b.shot(os.path.join(HERE, '_sat', 'tools_m_collapsed.png'))

    # ---------- раскрытие ----------
    b.js("document.getElementById('t-menu').click()")
    time.sleep(0.3)
    check('ряд раскрылся', b.js(OPEN) is True)
    check('☰ стал ✕', b.js("document.getElementById('t-menu').textContent") == '✕',
          b.js("document.getElementById('t-menu').textContent"))
    check('aria-expanded=true',
          b.js("document.getElementById('t-menu').getAttribute('aria-expanded')") == 'true')
    for bid in ('t-auto', 't-text', 't-voice', 't-music', 't-full'):
        check('раскрыто: %s виден' % bid, b.js(DISP % bid) != 'none', b.js(DISP % bid))
    b.shot(os.path.join(HERE, '_sat', 'tools_m_open.png'))

    # ---------- клик по тумблеру: свернул И переключил ----------
    b.js("document.getElementById('t-text').click()")
    time.sleep(0.25)
    check('клик по «Aa» свернул ряд', b.js(OPEN) is False)
    check('клик по «Aa» переключил текст',
          b.js("document.getElementById('stage').classList.contains('notext')") is True)
    b.js("document.getElementById('t-text').click()")  # вернуть текст как было

    # ---------- клик по кадру мимо тулбара ----------
    b.js("document.getElementById('t-menu').click()")
    time.sleep(0.2)
    check('раскрыли снова', b.js(OPEN) is True)
    b.js("document.getElementById('stage').click()")
    time.sleep(0.25)
    check('клик по кадру свернул ряд', b.js(OPEN) is False)

    # ---------- пауза остаётся доступной ----------
    # Авто по умолчанию ВКЛ (AUTO_DEFAULT = ?auto!=0), поэтому ⏸ виден сразу
    check('авто по умолчанию вкл (AUTO_DEFAULT)',
          b.js("document.getElementById('t-pause').hidden") is False)
    check('в авто ⏸ виден при свёрнутом ряде', b.js(DISP % 't-pause') != 'none',
          b.js(DISP % 't-pause'))
    b.shot(os.path.join(HERE, '_sat', 'tools_m_pause.png'))
    b.js("document.getElementById('t-pause').click()")
    time.sleep(0.2)
    check('⏸ нажимается при свёрнутом ряде (пауза встала)',
          b.js("document.getElementById('t-pause').textContent") == '▶',
          b.js("document.getElementById('t-pause').textContent"))
    b.js("document.getElementById('t-pause').click()")  # снять паузу
    time.sleep(0.2)
    b.js("document.getElementById('t-auto').click()")  # авто ВЫКЛ
    time.sleep(0.25)
    check('авто выкл → ⏸ скрыт и ряд свёрнут',
          b.js(DISP % 't-pause') == 'none' and b.js(OPEN) is False,
          b.js(DISP % 't-pause'))
    b.js("document.getElementById('t-auto').click()")  # авто обратно ВКЛ
    time.sleep(0.2)

    check('портрет: js-ошибок нет', not b.errors(), b.errors())

    # ---------- десктоп ----------
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900,
           deviceScaleFactor=1, mobile=False)
    b.send('Emulation.setTouchEmulationEnabled', enabled=False)
    b.navigate(BASE + '?preload=0')
    time.sleep(1.5)
    check('десктоп: медиазапрос портрета не активен',
          b.js("matchMedia('(max-aspect-ratio:1/1)').matches") is False)
    check('десктоп: ☰ скрыт', b.js(DISP % 't-menu') == 'none', b.js(DISP % 't-menu'))
    for bid in ('t-auto', 't-text', 't-voice', 't-music', 't-full'):
        check('десктоп: %s виден' % bid, b.js(DISP % bid) != 'none', b.js(DISP % bid))
    b.js("document.getElementById('start').click()")
    time.sleep(1.2)
    b.js("(function(){var v=document.getElementById('vskip'); if(v) v.click();})()")
    time.sleep(1.5)
    b.shot(os.path.join(HERE, '_sat', 'tools_d_desktop.png'))
    check('десктоп: js-ошибок нет', not b.errors(), b.errors())
finally:
    b.close()

print('\nИТОГ: ' + ('ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(0 if ok else 1)
