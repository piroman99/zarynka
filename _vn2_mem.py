# -*- coding: utf-8 -*-
"""Память предзагрузки + книжка-оглавление в тулбаре (Иван 2026-11-10).

1) кнопка «Оглавление» в тулбаре: на заставке спрятана, в игре видна;
2) клик по книжке открывает оглавление, страница при этом НЕ листается;
3) Esc закрывает, игра продолжается с той же страницы;
4) декодированные битмапы не превышают потолок (PL_CAP) и окно работает:
   после 40 страниц в памяти заметно меньше, чем «весь эпизод» (271 МБ);
5) промахов 404 нет, ошибок в консоли нет;
6) в портрете книжка живёт внутри ☰.
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
TITLE = "document.getElementById('title').classList.contains('show')"


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
    b.navigate(BASE)
    b.wait_js("!!window.__PL && !!window.__DBG", 30)
    time.sleep(4)                                   # даём стартовой предзагрузке улечься

    # ---------- 1. заставка ----------
    vis = "getComputedStyle(document.getElementById('t-toc')).display"
    check('на заставке книжка в тулбаре спрятана', b.js(vis) == 'none', b.js(vis))
    check('большая «Оглавление» на заставке видна',
          b.js("getComputedStyle(document.getElementById('toc-open')).display") != 'none')

    # ---------- 2. стартовая память ----------
    cap = b.js("__PL.cap()")
    start_bytes = b.js("__PL.bytes()")
    start_imgs = b.js("__PL.img.size")
    print('  заставка: %.1f МБ в %d картинках, потолок %.0f МБ' %
          (start_bytes / 1e6, start_imgs, cap / 1e6))
    check('на заставке держим меньше потолка', start_bytes <= cap, '%.1f МБ' % (start_bytes / 1e6))
    check('на заставке меньше 120 МБ (было 271)', start_bytes < 120e6, '%.1f МБ' % (start_bytes / 1e6))
    check('тизер не качается заранее (видео в кэше < 2)', b.js("__PL.vid.size") <= 1,
          b.js("JSON.stringify([...__PL.vid.keys()])"))
    check('очередь стартовой предзагрузки пуста', b.js("__PL.queue()") == 0, b.js("__PL.queue()"))

    # ---------- 3. игра: книжка в тулбаре ----------
    b.js("document.getElementById('start').click()")
    b.wait_js("document.getElementById('hud').classList.contains('on')", 40)
    time.sleep(1.5)
    check('в игре книжка видна', b.js(vis) != 'none', b.js(vis))

    pos_before = b.js("__DBG.pos")
    b.js("document.getElementById('t-toc').click()")
    time.sleep(0.4)
    check('книжка открыла оглавление', b.js("__TOC.shown") is True)
    check('страница не уехала от клика по книжке', b.js("__DBG.pos") == pos_before,
          '%s -> %s' % (pos_before, b.js("__DBG.pos")))
    check('игра стоит на паузе-меню (кадр не листается сам)',
          b.js("document.getElementById('toc').classList.contains('show')") is True)
    b.shot(os.path.join(HERE, '_sat', 'toc_from_game.png'))

    # Esc закрывает и возвращает в игру
    b.js("document.getElementById('toc').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))")
    b.js("window.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}))")
    time.sleep(0.4)
    check('Esc закрыл оглавление', b.js("__TOC.shown") is False)
    check('после Esc всё ещё в игре, та же страница', b.js("__DBG.pos") == pos_before,
          b.js("__DBG.pos"))

    # ---------- 4. листаем 40 страниц: окно и потолок ----------
    peak = 0
    for i in range(40):
        b.js("document.getElementById('stage').click()")
        if b.js("__DBG.typing"):
            b.js("document.getElementById('stage').click()")   # дописать фразу
        time.sleep(0.16)
        if i % 8 == 7:
            by = b.js("__PL.bytes()") or 0
            peak = max(peak, by)
    time.sleep(3)
    b.js("__PL.trim()")
    time.sleep(0.5)
    mid_bytes = b.js("__PL.bytes()")
    mid_pos = b.js("__DBG.pos")
    print('  после %d страниц: %.1f МБ в %d картинках (пик %.1f МБ)' %
          (mid_pos, mid_bytes / 1e6, b.js("__PL.img.size"), peak / 1e6))
    check('прошли хотя бы 20 страниц', mid_pos >= 20, mid_pos)
    check('память в потолке', mid_bytes <= cap, '%.1f МБ / %.0f МБ' % (mid_bytes / 1e6, cap / 1e6))
    check('память ниже 120 МБ', mid_bytes < 120e6, '%.1f МБ' % (mid_bytes / 1e6))
    check('пик по ходу чтения тоже в потолке', peak <= cap, '%.1f МБ' % (peak / 1e6))
    check('404 нет', b.js("__PL.miss.size") == 0, b.js("JSON.stringify([...__PL.miss])"))

    # ---------- 5. прыжок по оглавлению в дальнюю главу ----------
    b.js("__TOC.open()")
    time.sleep(0.3)
    b.js("__TOC.jump(100)")
    time.sleep(6)
    far_pos = b.js("__DBG.pos")
    check('прыжок в конец сработал', far_pos >= 95, far_pos)
    check('кадр на месте после прыжка (фон не пустой)',
          b.js("!!(document.getElementById('bg-a').style.backgroundImage || "
               "document.getElementById('bg-b').style.backgroundImage)") is True)
    check('после прыжка память в потолке', (b.js("__PL.bytes()") or 0) <= cap,
          '%.1f МБ' % ((b.js("__PL.bytes()") or 0) / 1e6))

    errs = [e for e in b.errors() if 'favicon' not in e]
    check('ошибок в консоли нет', not errs, errs[:3])
    b.shot(os.path.join(HERE, '_sat', 'mem_after_jump.png'))
finally:
    b.close()

# ---------- 6. портрет ----------
b = Browser(390, 844)
try:
    b.navigate(BASE)
    b.wait_js("!!window.__DBG", 30)
    time.sleep(1)
    b.js("document.getElementById('start').click()")
    b.wait_js("document.getElementById('hud').classList.contains('on')", 40)
    time.sleep(1)
    b.js("document.getElementById('t-menu').click()")
    time.sleep(0.4)
    check('в портрете книжка внутри ☰ (видна после раскрытия)',
          b.js("getComputedStyle(document.getElementById('t-toc')).display") != 'none',
          b.js("getComputedStyle(document.getElementById('t-toc')).display"))
    b.js("document.getElementById('t-toc').click()")
    time.sleep(0.4)
    check('книжка в портрете открывает оглавление', b.js("__TOC.shown") is True)
    b.shot(os.path.join(HERE, '_sat', 'toc_btn_portrait.png'))
    b.js("__TOC.close()")
    time.sleep(0.3)
    # ряд в портрете живёт открытым до явного сворачивания (вариант B, коммит 6b9a19d)
    check('ряд после закрытия оглавления ещё раскрыт (вариант B)',
          b.js("getComputedStyle(document.getElementById('t-toc')).display") != 'none')
    b.js("document.getElementById('t-menu').click()")
    time.sleep(0.4)
    check('☰ сворачивает ряд вместе с книжкой',
          b.js("getComputedStyle(document.getElementById('t-toc')).display") == 'none',
          b.js("getComputedStyle(document.getElementById('t-toc')).display"))
    errs = [e for e in b.errors() if 'favicon' not in e]
    check('в портрете ошибок нет', not errs, errs[:3])
finally:
    b.close()

srv.shutdown()
print('\nИТОГ:', 'всё зелёное' if ok else 'есть провалы')
sys.exit(0 if ok else 1)
