# -*- coding: utf-8 -*-
"""Скриншоты S4 до/после наезда камеры (проверка подписи у ТВ).
node=5 = S4 (0 титул, 1 значок, 2 s1, 3 s2, 4 s3, 5 s4).
wide: virtual-time-budget 700 мс (наезд стартует на 0.9 с) -> scale 1.0
zoom: instant=1 -> scale 1.5 сразу
"""
import os
import subprocess
import glob

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
from _chrome import CHROME   # noqa: E402  (путь ищется вверх, раскладка не важна)
BASE = 'file://' + os.path.join(ROOT, 'vn2', 'index.html') + '?node=5&text=1&voice=0&music=0'

for tag, extra, budget in (('wide', '', 700), ('zoom', '&instant=1', 2500)):
    out = os.path.join(ROOT, 'assets', 'review', 'review_113_s4_cap_%s.png' % tag)
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
           '--allow-file-access-from-files', '--window-size=1600,900',
           '--virtual-time-budget=%d' % budget, '--screenshot=' + out, BASE + extra]
    subprocess.run(cmd, check=True)
    print(tag, '->', os.path.relpath(out, HERE), os.path.getsize(out), 'B')
