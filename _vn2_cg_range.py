# -*- coding: utf-8 -*-
"""Регресс: CG-диапазоны и выход Екатерины (правки Ивана 2026-10-25).

Проверяем по живой странице (Playwright-харнесс _cdp):
  1) стр. 35..37 (SCRIPT_CAST) — CG rec_35 стоит фоном, спрайтов нет;
  2) стр. 59..61 — CG rec_48 стоит фоном, спрайтов нет;
  3) до и после диапазонов — обычный фон приёмной и спрайты на месте;
  4) Екатерины НЕТ на описании (стр. 21), появляется на приветствии (стр. 23).
"""
import os, sys, time, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

GEO = """
(function(){
  var bg=[].map.call(document.querySelectorAll('.bg.on'),
        function(e){return (getComputedStyle(e).backgroundImage||'').split('/').pop().replace(/["')]/g,'');});
  var sprites=[].filter.call(document.querySelectorAll('.sprite'),
        function(e){return getComputedStyle(e).opacity!=='0';}).map(function(e){return e.id||e.className;});
  return {bg:bg, sprites:sprites, tx:document.getElementById('text').textContent.trim().slice(0,44)};
})()
"""

ok = fail = 0


def chk(cond, msg, extra=''):
    global ok, fail
    if cond:
        ok += 1
        print('  OK   %s %s' % (msg, extra))
    else:
        fail += 1
        print('  FAIL %s %s' % (msg, extra))


# (page-параметр 1-based: page=N открывает страницу N-1), ожидаемый фон, спрайтов
CASES = [
    (21, 'reception.webp', 2, 'до CG (стр. 21, описание) — фон приёмной, оба спрайта'),
    (22, 'rec_35.webp', 0, 'стр. 22 → CG rec_35'),
    (23, 'rec_35.webp', 0, 'стр. 23 → CG rec_35 (держится)'),
    (24, 'reception.webp', 2, 'стр. 24 → снова фон + спрайты'),
    (48, 'rec_48.webp', 0, 'стр. 48 → CG rec_48'),
    (49, 'rec_48.webp', 0, 'стр. 49 → CG rec_48 (продлён до 61)'),
    (50, 'rec_48.webp', 0, 'стр. 50 → CG rec_48 (конец диапазона)'),
    (51, 'reception.webp', 2, 'стр. 51 → снова фон + спрайты'),
]

# ВАЖНО: auto=0 — иначе короткие страницы сами уезжают за время ожидания и замер
# попадает на следующую страницу (на этом тест уже один раз соврал).
# Номер узла не хардкодим: при вставке кадров индексы СДВИГАЮТСЯ (было 11, после
# вставки кадра p6 приёмная стала 12) — берём из content.js по id.
from _vn2_nodes import node_index  # noqa: E402
REC = node_index('reception')
print('приёмная = node=%d' % REC)
URL = BASE + '?instant=1&auto=0&text=1&voice=0&music=0&node=%d&page=%%d' % REC

b = Browser(1280, 720)
try:
    for page, want_bg, want_sp, label in CASES:
        b.navigate(URL % page, wait=1.4)
        time.sleep(0.25)
        g = b.js(GEO)
        got = g['bg'][0] if g['bg'] else '(нет)'
        chk(got == want_bg and len(g['sprites']) == want_sp, label,
            'bg=%s sprites=%d' % (got, len(g['sprites'])))
    # выход Екатерины: на описании её нет, на приветствии есть
    b.navigate(URL % 3, wait=1.4)
    time.sleep(0.25)
    g = b.js(GEO)
    chk(len(g['sprites']) == 1, 'стр. 21 (описание): Екатерины ещё нет — только Сергей',
        'sprites=%d' % len(g['sprites']))
    b.navigate(URL % 5, wait=1.4)
    time.sleep(0.25)
    g = b.js(GEO)
    chk(len(g['sprites']) == 2, 'стр. 23 (приветствие): Екатерина вошла',
        'sprites=%d' % len(g['sprites']))
finally:
    b.close()
    srv.shutdown()

print('\nИТОГ: OK=%d FAIL=%d — %s' % (ok, fail, 'ВСЁ ЗЕЛЁНОЕ' if not fail else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(1 if fail else 0)
