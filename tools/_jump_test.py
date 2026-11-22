# -*- coding: utf-8 -*-
"""Проверка пасхалки «iddqd» в живом движке (headless Chromium через CDP).

Что проверяем:
  1) панель скрыта при запуске;
  2) набор iddqd на клавиатуре её открывает (и на русской раскладке тоже);
  3) подсказка показывает «где я сейчас»;
  4) переход по номеру страницы работает и НЕ двигает прогресс;
  5) «alley 4» — узел + страница внутри узла;
  6) мусор в поле — понятная ошибка, ничего не переходит;
  7) Esc закрывает;
  8) пять тапов по названию главы открывают панель;
  9) запуск с заставки (ещё не начато) — переход сразу стартует игру.
"""
import functools
import http.server
import os
import socketserver
import sys
import threading
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402

OUT = os.path.join(ROOT, '_sat')
os.makedirs(OUT, exist_ok=True)

VK = {'KeyI': 73, 'KeyD': 68, 'KeyQ': 81, 'Escape': 27}


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
    print('%-52s %s %s' % (name, 'OK' if cond else '!!! ПРОВАЛ', extra))
    if not cond:
        fails.append(name)


def key(b, code, k=None):
    b.send('Input.dispatchKeyEvent', type='keyDown', code=code, key=k or code[-1].lower(),
           windowsVirtualKeyCode=VK.get(code, 0), nativeVirtualKeyCode=VK.get(code, 0))
    b.send('Input.dispatchKeyEvent', type='keyUp', code=code, key=k or code[-1].lower(),
           windowsVirtualKeyCode=VK.get(code, 0), nativeVirtualKeyCode=VK.get(code, 0))


def wait_node(b, want, timeout=8.0):
    end = time.time() + timeout
    while time.time() < end:
        if b.js('window.__DBG ? window.__DBG.node : -1') == want:
            return True
        time.sleep(0.2)
    return False


def state(b):
    return b.js("""(function(){
      var j=document.getElementById('jump');
      return {shown:j.classList.contains('show'),
              hint:document.getElementById('jump-hint').textContent,
              bad:document.getElementById('jump-hint').classList.contains('bad'),
              val:document.getElementById('jump-in').value,
              pos:(window.__DBG?window.__DBG.pos:-1),
              node:(window.__DBG?window.__DBG.node:-1),
              max:(window.__TOC?window.__TOC.max:-9),
              started:(window.__DBG?window.__DBG.started:false)};
    })()""")


def type_text(b, s):
    b.js("document.getElementById('jump-in').value=%r;" % s)


def submit(b):
    b.js("document.getElementById('jump-form').dispatchEvent(new Event('submit',{cancelable:true}));")


def wait_pos(b, want, timeout=8.0):
    """Ждём, пока движок встанет на нужную страницу.

    Переход идёт через tocJump: он греет предзагрузку кадров до 2.5 с,
    поэтому сразу после submit проверять pos бессмысленно.
    """
    end = time.time() + timeout
    while time.time() < end:
        if b.js('window.__DBG ? window.__DBG.pos : -1') == want:
            return True
        time.sleep(0.2)
    return False


b = Browser(1440, 900)
try:
    # ---------- сценарий 1: с заставки ----------
    b.navigate(BASE + '?instant=1&auto=0&voice=0&music=0', wait=2.5)
    s = state(b)
    check('панель скрыта при запуске', not s['shown'])
    check('прогресс пустой (max = -1)', s['max'] == -1, str(s['max']))

    for code in ('KeyI', 'KeyD', 'KeyD', 'KeyQ', 'KeyD'):
        key(b, code)
    s = state(b)
    check('iddqd открывает панель', s['shown'])
    check('подсказка про «ещё не начато»', 'ещё не начато' in s['hint'], s['hint'][:60])
    b.shot(os.path.join(OUT, 'jump_title.png'))

    # ---------- переход с заставки ----------
    type_text(b, '40')
    submit(b)
    landed = wait_pos(b, 39)
    s = state(b)
    check('панель закрылась после перехода', not s['shown'])
    check('игра стартовала и встала на стр. 40', landed and s['started'],
          'pos=%s started=%s' % (s['pos'], s['started']))
    check('прогресс НЕ сдвинулся', s['max'] == -1, 'max=%s' % s['max'])

    # ---------- сценарий 2: русская раскладка ----------
    b.navigate(BASE + '?instant=1&auto=0&voice=0&music=0', wait=2.0)
    ru = {'KeyI': 'ш', 'KeyD': 'в', 'KeyQ': 'й'}
    for code in ('KeyI', 'KeyD', 'KeyD', 'KeyQ', 'KeyD'):
        key(b, code, ru[code])
    s = state(b)
    check('iddqd на русской раскладке тоже работает', s['shown'])

    # ---------- узел + страница ----------
    type_text(b, 'alley 4')
    submit(b)
    landed = wait_node(b, 16)
    s = state(b)
    # номер страницы ВНУТРИ узла берём у самого движка: открываем панель и читаем подсказку
    for code in ('KeyI', 'KeyD', 'KeyD', 'KeyQ', 'KeyD'):
        key(b, code)
    hint = state(b)['hint']
    key(b, 'Escape', 'Escape')
    check('«alley 4» переводит в узел alley', landed and s['node'] == 16,
          'node=%s pos=%s' % (s['node'], s['pos']))
    check('«alley 4» встаёт именно на 4-ю страницу узла', 'стр. 4)' in hint, hint[:80])
    check('прогресс всё ещё не тронут', s['max'] == -1, 'max=%s' % s['max'])
    b.shot(os.path.join(OUT, 'jump_alley4.png'))

    # ---------- мусор ----------
    for code in ('KeyI', 'KeyD', 'KeyD', 'KeyQ', 'KeyD'):
        key(b, code)
    s = state(b)
    check('панель открылась повторно', s['shown'])
    check('подсказка «сейчас» с узлом', 'сейчас' in s['hint'], s['hint'][:70])
    type_text(b, 'чепуха')
    submit(b)
    time.sleep(0.4)
    s2 = state(b)
    check('мусор: панель осталась открыта', s2['shown'])
    check('мусор: подсказка красная', s2['bad'], s2['hint'][:70])
    check('мусор: никуда не перешли', s2['pos'] == s['pos'], '%s -> %s' % (s['pos'], s2['pos']))
    b.shot(os.path.join(OUT, 'jump_bad.png'))

    # ---------- Esc ----------
    key(b, 'Escape', 'Escape')
    s = state(b)
    check('Esc закрывает панель', not s['shown'])

    # ---------- пять тапов по названию главы ----------
    b.js("""(function(){var c=document.getElementById('chapter');
      for(var i=0;i<5;i++) c.dispatchEvent(new MouseEvent('click',{bubbles:true}));
    })()""")
    time.sleep(0.3)
    s = state(b)
    check('5 тапов по названию главы открывают панель', s['shown'])

    # ---------- переход по абсолютному номеру и печать дальше ----------
    type_text(b, '1')
    submit(b)
    landed = wait_pos(b, 0)
    s = state(b)
    check('переход на стр. 1', landed, 'pos=%s' % s['pos'])
    b.js("document.getElementById('next').click()")
    time.sleep(0.8)
    s = state(b)
    check('после пасхалки прогресс по-прежнему не пишется', s['max'] == -1,
          'max=%s pos=%s' % (s['max'], s['pos']))

    errs = b.errors()
    check('нет ошибок JS', not errs, '; '.join(errs[:3]))
finally:
    b.close()
    srv.shutdown()

print('\nпровалов: %d %s' % (len(fails), fails if fails else ''))
print('OUT', OUT)
sys.exit(0 if not fails else 1)
