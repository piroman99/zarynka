# -*- coding: utf-8 -*-
"""Проверка JS движка: гоняем headless Chromium с логом консоли и ищем ошибки.
Плюс dump-dom: убеждаемся, что init дошёл до конца (поле #tep заполнено из content.js).
"""
import os, subprocess, glob, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]

query = sys.argv[1] if len(sys.argv) > 1 else '?preload=0'
url = 'file://' + os.path.join(HERE, 'vn2', 'index.html') + query

cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
       '--allow-file-access-from-files', '--virtual-time-budget=4000',
       '--enable-logging=stderr', '--log-level=0', '--dump-dom', url]
p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
err = p.stderr or ''

bad = [ln for ln in err.splitlines()
       if re.search(r'Uncaught|SyntaxError|ReferenceError|TypeError|CONSOLE.*(error|Error)', ln)
       and 'dbus' not in ln and 'ALSA' not in ln and 'Fontconfig' not in ln]
print('ошибок JS:', len(bad))
for b in bad[:12]:
    print('   ', b[:300])

dom = p.stdout or ''
m = re.search(r'id="tep"[^>]*>([^<]*)<', dom)
print('init дошёл (#tep =', (m.group(1) if m else 'НЕ НАЙДЕН'), ')')
m2 = re.search(r'id="byline"[^>]*>([^<]*)<', dom)
print('byline =', (m2.group(1) if m2 else 'НЕ НАЙДЕН'))
m3 = re.search(r'id="pltext"[^>]*>([^<]*)<', dom)
print('pltext =', repr(m3.group(1) if m3 else 'НЕ НАЙДЕН'))
