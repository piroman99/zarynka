# -*- coding: utf-8 -*-
"""Проверка пасхалки iddqd на ЖИВОМ демо GitHub Pages (не локально)."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402

URL = 'https://piroman99.github.io/zarynka/vn2/?instant=1&auto=0&voice=0&music=0'
VK = {'KeyI': 73, 'KeyD': 68, 'KeyQ': 81}


def key(b, code):
    b.send('Input.dispatchKeyEvent', type='keyDown', code=code, key=code[-1].lower(),
           windowsVirtualKeyCode=VK[code], nativeVirtualKeyCode=VK[code])
    b.send('Input.dispatchKeyEvent', type='keyUp', code=code, key=code[-1].lower(),
           windowsVirtualKeyCode=VK[code], nativeVirtualKeyCode=VK[code])


fails = []


def check(name, cond, extra=''):
    print('%-48s %s %s' % (name, 'OK' if cond else '!!! ПРОВАЛ', extra))
    if not cond:
        fails.append(name)


b = Browser(1440, 900)
try:
    b.navigate(URL, wait=6.0)
    has = b.js("!!document.getElementById('jump')")
    check('на живом демо есть панель #jump', has)
    if has:
        for code in ('KeyI', 'KeyD', 'KeyD', 'KeyQ', 'KeyD'):
            key(b, code)
        time.sleep(0.4)
        shown = b.js("document.getElementById('jump').classList.contains('show')")
        hint = b.js("document.getElementById('jump-hint').textContent")
        check('iddqd открывает панель на живом демо', shown)
        check('подсказка живая', bool(hint), hint[:70])
        b.js("document.getElementById('jump-in').value='alley 4';"
             "document.getElementById('jump-form').dispatchEvent(new Event('submit',{cancelable:true}));")
        end = time.time() + 12
        pos = -1
        while time.time() < end:
            pos = b.js('window.__DBG ? window.__DBG.pos : -1')
            if pos == 80:
                break
            time.sleep(0.3)
        node = b.js('window.__DBG ? window.__DBG.node : -1')
        mx = b.js('window.__TOC ? window.__TOC.max : -9')
        check('переход «alley 4» на живом демо', node == 16, 'node=%s pos=%s' % (node, pos))
        check('прогресс не тронут', mx == -1, 'max=%s' % mx)
        b.shot(os.path.join(ROOT, '_sat', 'jump_live.png'))
        errs = b.errors()
        check('нет ошибок JS', not errs, '; '.join(errs[:2]))
finally:
    b.close()

print('\nпровалов: %d %s' % (len(fails), fails if fails else ''))
sys.exit(0 if not fails else 1)
