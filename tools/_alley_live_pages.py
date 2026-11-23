# -*- coding: utf-8 -*-
"""Живое демо Pages: сцена «аллея» с новой скамейкой. Проверяет, что на живом
сайте проп грузится и красится, и снимает кадр в размере телефона.

Запуск: python3 tools/_alley_live_pages.py [node] [page]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAT = os.path.join(ROOT, '_sat')
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402

node = int(sys.argv[1]) if len(sys.argv) > 1 else 16
page = int(sys.argv[2]) if len(sys.argv) > 2 else 0
URL = ('https://piroman99.github.io/zarynka/vn2/?node=%d&page=%d'
       '&instant=1&text=1&voice=0&music=0' % (node, page))

JS = ("(function(){var p=document.querySelector('#props .prop');"
      "var b=document.querySelector('.bg.on');"
      "return {prop: !!p && p.classList.contains('on'), nat: p?[p.naturalWidth,p.naturalHeight]:null,"
      "bg: b?b.style.backgroundImage:'', txt:(document.getElementById('text')||{}).textContent};})()")

b = Browser(390, 844)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=390, height=844,
           deviceScaleFactor=2, mobile=True)
    b.navigate(URL, wait=4.0)
    b.wait_js("!!document.querySelector('#props .prop.on')", timeout=25)
    info = b.js(JS)
    out = os.path.join(SAT, 'alley_pages_phone.png')
    b.shot(out)
    errs = b.errors()
finally:
    b.close()

print('живое демо:', URL)
for k, v in info.items():
    print('   %-5s %s' % (k, str(v)[:90]))
print('   js-ошибок: %s' % (errs if errs else 'нет'))
print('   кадр:', os.path.relpath(out, ROOT))
