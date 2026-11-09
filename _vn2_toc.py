# -*- coding: utf-8 -*-
"""Оглавление «как в книге» + память прогресса (запрос Ивана 2026-11-09).

Проверяем:
  1) на заставке три кнопки: «Начать», «Оглавление», «Тизер» — все видимы;
  2) оглавление открывается, 4 главы, счёт страниц 14/4/57/41 = 116;
  3) на чистом профиле всё заперто (замки), заметка «ещё не начато»;
  4) Esc закрывает; клик по запертой строке ничего не запускает;
  5) сброс прогресса в два шага (первый клик — «Точно?»);
  6) прошли несколько страниц → перезагрузка → «Продолжить» с номером страницы;
  7) в оглавлении пройденное разблокировано и с ✓, непройденное — под замком;
  8) клик по главе «Пролог» запускает новеллу с её первой страницы;
  9) нет ошибок в консоли.

Скриншоты: _sat/toc_desktop.png, toc_mobile.png, toc_progress.png
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
Q = "document.querySelectorAll"
TOC_SHOW = "document.getElementById('toc').classList.contains('show')"
TITLE_SHOW = "document.getElementById('title').classList.contains('show')"


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

b = Browser(1600, 900)
try:
    b.navigate(BASE + '?preload=0')
    time.sleep(1.5)

    # ---------- 1. заставка ----------
    check('«Начать» на месте', b.js("document.getElementById('start').textContent") == 'Начать',
          b.js("document.getElementById('start').textContent"))
    check('«Оглавление» видно',
          b.js("getComputedStyle(document.getElementById('toc-open')).display") != 'none')
    check('«Тизер» видно',
          b.js("getComputedStyle(document.getElementById('teaser')).display") != 'none')
    check('оглавление сначала закрыто', b.js(TOC_SHOW) is False)

    # ---------- 2. открытие ----------
    b.js("document.getElementById('toc-open').click()")
    time.sleep(0.5)
    check('открылось', b.js(TOC_SHOW) is True)
    check('aria-hidden снят', b.js("document.getElementById('toc').getAttribute('aria-hidden')") == 'false')
    check('глав 4', b.js(Q + "('#toclist .toc-chaprow').length") == 4,
          b.js(Q + "('#toclist .toc-chaprow').length"))
    counts = b.js("window.__TOC.counts()")
    print('       счёт по главам:', counts)
    check('счёт страниц 14/4/57/41',
          counts == ['Пролог:14', 'Кабинет Старика:4', 'Приёмная:57', 'Аллея у ворот:41'], counts)
    check('подпунктов 12 (10 пролога + 2 аллеи)', b.js(Q + "('#toclist .toc-sub .toc-row').length") == 12,
          b.js(Q + "('#toclist .toc-sub .toc-row').length"))
    check('заметка «ещё не начато»',
          'ещё не начато' in (b.js("document.getElementById('tocnote').textContent") or ''),
          b.js("document.getElementById('tocnote').textContent"))
    rows = b.js(Q + "('#toclist button').length")
    locked = b.js(Q + "('#toclist button:disabled').length")
    check('на чистом профиле всё под замком', locked == rows and rows == 16, '%d/%d' % (locked, rows))
    check('в главе есть первая фраза',
          len(b.js(Q + "('#toclist .toc-chaprow .sn')[0].textContent") or '') > 10,
          b.js(Q + "('#toclist .toc-chaprow .sn')[0].textContent"))
    b.shot(os.path.join(HERE, '_sat', 'toc_desktop.png'))

    # ---------- 4. запертая строка не запускает ----------
    b.js(Q + "('#toclist .toc-sub .toc-row')[0].click()")
    time.sleep(0.4)
    check('клик по замку не запустил новеллу', b.js(TITLE_SHOW) is True)
    check('и оглавление осталось открытым', b.js(TOC_SHOW) is True)

    # ---------- 4. Esc ----------
    b.js("window.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))")
    time.sleep(0.4)
    check('Esc закрыл оглавление', b.js(TOC_SHOW) is False)
    check('вернулись на заставку', b.js(TITLE_SHOW) is True)

    # ---------- 5. сброс в два шага ----------
    b.js("document.getElementById('toc-open').click()")
    time.sleep(0.3)
    b.js("document.getElementById('toc-reset').click()")
    time.sleep(0.3)
    t1 = b.js("document.getElementById('toc-reset').textContent")
    check('первый клик — только предупреждение', 'Точно?' in (t1 or ''), t1)
    b.js("document.getElementById('toc-reset').click()")
    time.sleep(0.3)
    t2 = b.js("document.getElementById('toc-reset').textContent")
    check('второй клик вернул подпись', t2 == 'Сбросить прогресс', t2)
    b.js("document.getElementById('toc-x').click()")
    time.sleep(0.3)

    # ---------- 6. играем и запоминаем ----------
    b.js("document.getElementById('start').click()")
    time.sleep(1.2)
    b.js("document.getElementById('vskip').click()")
    time.sleep(1.0)
    b.js("window.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))")   # посвящение
    time.sleep(0.8)
    for _ in range(14):
        if b.js("window.__DBG.pos") >= 3:
            break
        b.js("window.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight'}))")
        time.sleep(0.45)
    pos = b.js("window.__DBG.pos")
    mx = b.js("window.__TOC.max")
    check('дошли до 4-й страницы', pos >= 3, 'pos=%s max=%s' % (pos, mx))
    check('прогресс записан в localStorage',
          'zaryanka.progress' in (b.js("Object.keys(localStorage).join(',')") or ''),
          b.js("Object.keys(localStorage).join(',')"))

    b.navigate(BASE + '?preload=0')
    time.sleep(1.5)
    check('после перезагрузки кнопка «Продолжить»',
          b.js("document.getElementById('start').textContent") == 'Продолжить',
          b.js("document.getElementById('start').textContent"))
    check('в подсказке номер страницы',
          'страницы' in (b.js("document.getElementById('start').title") or ''),
          b.js("document.getElementById('start').title"))

    # ---------- 7. разблокировка в оглавлении ----------
    b.js("document.getElementById('toc-open').click()")
    time.sleep(0.5)
    note = b.js("document.getElementById('tocnote').textContent")
    check('заметка о прогрессе', 'пройдено до стр.' in (note or ''), note)
    ch0 = b.js(Q + "('#toclist .toc-chaprow')[0]")
    check('первая глава разблокирована', b.js(Q + "('#toclist .toc-chaprow')[0].disabled") is False)
    check('на первой главе галочка',
          b.js(Q + "('#toclist .toc-chaprow')[0].classList.contains('done')") is True)
    sub = b.js(Q + "('#toclist .toc-sub .toc-row')")
    states = b.js("Array.from(" + Q + "('#toclist .toc-sub .toc-row')).slice(0,3)"
                  ".map(function(b){return b.dataset.node+':'+(b.disabled?'lock':'open')})")
    print('       первые узлы:', states)
    check('s1 открыт, p7 ещё заперт', states[0] == 's1:open' and states[2] == 'p7:lock', states)
    b.shot(os.path.join(HERE, '_sat', 'toc_progress.png'))

    # ---------- 8. клик по главе запускает с её первой страницы ----------
    b.js(Q + "('#toclist .toc-chaprow')[0].click()")
    time.sleep(1.2)
    check('новелла запустилась', b.js(TITLE_SHOW) is False)
    check('и открылась 1-я страница', b.js("window.__DBG.pos") == 0, b.js("window.__DBG.pos"))
    check('оглавление закрылось', b.js(TOC_SHOW) is False)

    # ---------- 9. портрет ----------
    b.send('Emulation.setDeviceMetricsOverride', width=390, height=844,
           deviceScaleFactor=2, mobile=True)
    b.send('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=5)
    b.navigate(BASE + '?preload=0')
    time.sleep(1.5)
    b.js("document.getElementById('toc-open').click()")
    time.sleep(0.6)
    check('портрет: оглавление открылось', b.js(TOC_SHOW) is True)
    fits = b.js("(function(){var l=document.getElementById('toclist');"
                "return l.scrollHeight<=l.clientHeight+2})()")
    print('       портрет: список целиком влезает =', fits,
          'scrollH/clientH =', b.js("(function(){var l=document.getElementById('toclist');"
                                    "return l.scrollHeight+'/'+l.clientHeight})()"))
    check('портрет: ни одна строка не вылезает за экран',
          b.js("(function(){var r=document.getElementById('toc').getBoundingClientRect();"
               "return r.width>0&&r.height>0&&r.bottom<=844.5})()") is True)
    b.shot(os.path.join(HERE, '_sat', 'toc_mobile.png'))

    errs = b.errors()
    check('ошибок в консоли нет', not errs, errs[:3])
finally:
    b.close()
    srv.shutdown()

print()
print('ИТОГ:', 'ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОВАЛЫ')
sys.exit(0 if ok else 1)
