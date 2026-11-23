# -*- coding: utf-8 -*-
"""Проверка: на CG-странице «Муза» (узел 16, стр. 18) проп-скамейка скрыт,
а на соседней обычной странице — виден. Ждём именно нужный фон, а не «что-то».

Запуск: python3 tools/_alley_cg_prop.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402

BASE = 'file://' + os.path.join(ROOT, 'vn2', 'index.html')
PROP_ON = ("(function(){var p=document.querySelector('#props .prop');"
           "return !!(p && p.classList.contains('on'));})()")
BG = "(function(){var b=document.querySelector('.bg.on');return b?b.style.backgroundImage:'';})()"

b = Browser(1280, 720)
try:
    for page, expect in ((18, False), (17, True), (19, True)):
        b.navigate(BASE + '?node=16&page=%d&instant=1&text=1&voice=0&music=0' % page, wait=2.5)
        b.wait_js("(document.querySelector('.bg.on')||{}).style.backgroundImage !== ''", timeout=20)
        bg = b.js(BG)
        on = b.js(PROP_ON)
        print('стр. %2d  фон %-28s проп %-5s  ожидалось %-5s  %s'
              % (page, (bg or '')[:28], on, expect, 'OK' if on == expect else '!!!'))
finally:
    b.close()
