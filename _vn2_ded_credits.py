# -*- coding: utf-8 -*-
"""Регресс: посвящение после значка + титры-ролл в конце + CG-страница.

Проверяем то, что просил Иван 2026-10-24:
  1) после лого-значка идёт посвящение (текст дословно из рассказа), затем пролог;
  2) в конце серии титры открываются САМИ, листаются роллом и уступают экрану «Конец»;
  3) в титрах есть Иван (piroman99) и nanobot, и НЕТ придуманных должностей;
  4) страница 48 приёмной — CG-кадр (вариант А) без спрайтов поверх.
"""
import os
import re
import sys
import time
import threading
import functools
import http.server
import socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser
from _vn2_nodes import node_index   # индекс узла из content.js, не хардкод
REC = node_index('reception')       # было 11; после вставки кадра p6 стало 12

ok = True


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

ST = ("[document.getElementById('ded').classList.contains('show'),"
      " document.getElementById('credits').classList.contains('show'),"
      " document.getElementById('end').classList.contains('show'),"
      " __DBG.pos, document.getElementById('vlayer').hidden]")

b = Browser(1280, 720)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1280, height=720,
           deviceScaleFactor=1, mobile=False)

    # ---------- 1) значок → посвящение → пролог ----------
    b.navigate(BASE + '?preload=0&auto=0')
    time.sleep(1.0)
    b.js("document.getElementById('start').click()")
    time.sleep(1.2)
    check('после «Начать» идёт значок-видео',
          b.js("document.getElementById('vlayer').hidden") is False)
    b.js("document.getElementById('vskip').click()")
    time.sleep(0.6)
    st = b.js(ST)
    check('после значка — посвящение', st[0] is True, st)
    l1 = b.js("document.getElementById('ded-l1').textContent")
    l2 = b.js("document.getElementById('ded-l2').textContent")
    check('первая строка посвящения верная', l1 == 'Посвящается Екатерине Ивановне Жадан', l1)
    check('вторая строка посвящения верная',
          l2 == 'бескорыстному врачу и человеку большого сердца', l2)
    check('пролог ещё не начался', st[3] in (0, None), 'pos=%s' % st[3])

    # клик по сцене уводит к прологу
    b.js("document.getElementById('ded').click()")
    time.sleep(0.8)
    st = b.js(ST)
    check('клик закрывает посвящение', st[0] is False, st)
    check('после посвящения — первая страница', st[3] == 0, 'pos=%s' % st[3])

    # ---------- 2) посвящение уходит само в авто-режиме ----------
    b.navigate(BASE + '?preload=0&auto=1')
    time.sleep(1.0)
    b.js("document.getElementById('start').click()")
    time.sleep(1.0)
    b.js("document.getElementById('vskip').click()")
    time.sleep(0.4)
    check('в авто-режиме посвящение показано',
          b.js("document.getElementById('ded').classList.contains('show')") is True)
    gone = None
    t0 = time.time()
    while time.time() - t0 < 12:
        if b.js("document.getElementById('ded').classList.contains('show')") is False:
            gone = time.time() - t0
            break
        time.sleep(0.4)
    check('в авто-режиме посвящение уходит само', gone is not None,
          '%.1f с' % gone if gone else 'не ушло')

    # ---------- 3) конец серии → титры сами ----------
    b.navigate(BASE + '?preload=0&auto=0&node=%d&page=56' % REC, wait=1.4)
    # первый клик может только дописать текст страницы — жмём до перехода
    for _ in range(4):
        b.js("document.getElementById('next').click()")
        time.sleep(0.5)
        if b.js("document.getElementById('credits').classList.contains('show')"):
            break
    st = b.js(ST)
    check('в конце серии титры открылись сами', st[1] is True, st)
    check('экран «Конец» под титрами скрыт', st[2] is False, st)
    check('ролл запущен', b.js("document.getElementById('crlist').classList.contains('run')") is True)
    dur = b.js("getComputedStyle(document.getElementById('crlist')).animationDuration")
    check('ролл не мгновенный и не бесконечный', dur and 8 < float(dur[:-1]) < 95, dur)

    txt = b.js("document.getElementById('crlist').textContent") or ''
    check('в титрах есть Иван (piroman99)', 'piroman99' in txt and 'Иван Карпухин' in txt)
    check('в титрах есть nanobot', 'nanobot' in txt)
    bad = [w for w in ('режисс', 'продюсер', 'руководитель проекта') if w in txt.lower()]
    check('нет придуманных должностей', not bad, bad)
    check('титры упоминают автора рассказа', 'Котобус' in txt)

    # мерцающие звёзды в титрах (2026-10-25): три слоя, анимация реально идёт
    stars = b.js("(function(){var s=document.querySelector('.cr-stars');"
                 "if(!s) return null;"
                 "var l=[].map.call(s.children,function(e){var c=getComputedStyle(e);"
                 "return c.animationName+'|'+c.animationDuration+'|'"
                 "+(c.backgroundImage.match(/radial-gradient/g)||[]).length;});"
                 "return {n:l.length, l:l};})()")
    check('звёзды: три слоя', stars and stars['n'] == 3, stars and stars['n'])
    if stars:
        names = [x.split('|')[0] for x in stars['l']]
        durs = [x.split('|')[1] for x in stars['l']]
        dots = [int(x.split('|')[2]) for x in stars['l']]
        check('звёзды мерцают (crTwinkle)', all(n == 'crTwinkle' for n in names), names)
        check('у слоёв разная частота', len(set(durs)) == 3, durs)
        check('звёзд достаточно (150+)', sum(dots) >= 150, dots)

    # пропуск титров → экран конца серии
    b.js("document.getElementById('cr-skip').click()")
    time.sleep(0.8)
    st = b.js(ST)
    check('после пропуска титров — экран «Конец»', st[2] is True, st)
    check('титры закрыты', st[1] is False, st)

    # кнопка «Титры» на экране конца возвращает ролл
    b.js("document.getElementById('e-credits').click()")
    time.sleep(0.6)
    st = b.js(ST)
    check('кнопка «Титры» открывает ролл заново', st[1] is True, st)

    # ---------- 4) CG-страница приёмной ----------
    b.navigate(BASE + '?preload=0&auto=0&node=%d&page=48' % REC, wait=1.4)
    bg = b.js("[].map.call(document.querySelectorAll('.bg'),function(e){return e.style.backgroundImage})"
              ".filter(Boolean).join(' ')")
    check('CG-кадр стоит фоном страницы 48', 'cg/rec_48' in bg, bg[:80])
    sprites = b.js("[].filter.call(document.querySelectorAll('.sprite'),"
                   "function(e){return getComputedStyle(e).opacity!=='0'}).length")
    check('поверх CG спрайтов нет', sprites == 0, 'спрайтов: %s' % sprites)

    check('js-ошибок нет', not b.errors(), b.errors())
finally:
    b.close()
    srv.shutdown()

print('\nИТОГ: ' + ('ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(0 if ok else 1)
