# -*- coding: utf-8 -*-
"""Живая проверка сворачиваемого тулбара на демо GitHub Pages (портрет 390x844)."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

LIVE = 'https://piroman99.github.io/zarynka/vn2/index.html'
DISP = "(function(){var e=document.getElementById('%s');return getComputedStyle(e).display})()"
OPEN = "document.getElementById('tools').classList.contains('open')"
ok = True


def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK   ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))


b = Browser(390, 844)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=390, height=844,
           deviceScaleFactor=2, mobile=True)
    b.send('Emulation.setTouchEmulationEnabled', enabled=True, maxTouchPoints=5)
    b.navigate(LIVE + '?preload=0')
    time.sleep(3.0)
    check('☰ есть на демо', b.js(DISP % 't-menu') != 'none', b.js(DISP % 't-menu'))
    check('ряд свёрнут на старте', b.js(OPEN) is False)
    b.js("document.getElementById('start').click()")
    time.sleep(2.5)
    b.js("(function(){var v=document.getElementById('vskip'); if(v) v.click();})()")
    time.sleep(2.0)
    b.js("document.getElementById('t-menu').click()")
    time.sleep(0.4)
    check('☰ раскрывает ряд', b.js(OPEN) is True)
    b.js("document.getElementById('t-text').click()")
    time.sleep(0.4)
    check('Aa не сворачивает (вариант B)', b.js(OPEN) is True)
    b.js("document.getElementById('t-text').click()")
    b.js("document.getElementById('stage').click()")
    time.sleep(0.4)
    check('клик по кадру не сворачивает', b.js(OPEN) is True)
    b.js("document.getElementById('t-menu').click()")
    time.sleep(0.3)
    check('✕ сворачивает', b.js(OPEN) is False)
    b.shot(os.path.join(HERE, '_sat', 'tools_live_collapsed.png'))
    b.js("document.getElementById('t-menu').click()")
    time.sleep(0.3)
    b.shot(os.path.join(HERE, '_sat', 'tools_live_open.png'))
    errs = [e for e in b.errors() if 'net::' not in e]
    check('js-ошибок нет (сетевые отброшены)', not errs, errs[:3])
finally:
    b.close()

print('\nИТОГ: ' + ('ДЕМО РАБОТАЕТ КАК ЛОКАЛЬНО' if ok else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(0 if ok else 1)
