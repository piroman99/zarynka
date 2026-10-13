# -*- coding: utf-8 -*-
"""Проверка НАЕЗДА в реальном движке: headless Chromium, кадр S4 (node=5).
Бит1 — бюджет 700 мс (удержание ещё идёт), бит2 — 6000 мс (наезд завершён)."""
import os, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = os.path.join(WS, '.playwright-browsers', 'chromium-1243', 'chrome-linux64', 'chrome')
OUT = os.path.join(HERE, 'assets', 'review')
idx = os.path.join(HERE, 'vn2', 'index.html')
url = 'file://' + idx + '?node=5'

print('chrome:', os.path.exists(CHROME))


def shot(budget, name):
    p = os.path.join(OUT, name)
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
           '--allow-file-access-from-files', '--window-size=1600,900',
           '--virtual-time-budget=%d' % budget, '--screenshot=' + p, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(name, 'rc=', r.returncode, 'exists=', os.path.exists(p),
          (r.stderr or '')[-200:] if r.returncode else '')


shot(700, '_tmp_engine_b1.png')
shot(6500, '_tmp_engine_b2.png')
