# -*- coding: utf-8 -*-
"""Живой кадр CG-страницы «Муза» в игре: vn2, узел «аллея», страница 18 (1280x720).

Запуск: python3 tools/_alley_cg_shot.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser  # noqa: E402
from _vn2_nodes import node_index  # noqa: E402

BASE = 'file://' + os.path.join(ROOT, 'vn2', 'index.html')
AL = node_index('alley')
OUT = os.path.join(ROOT, '_sat', 'cg_muza5_live.png')

b = Browser(1280, 720)
try:
    b.navigate(BASE + '?node=%d&page=18&instant=1&auto=0&text=1&voice=0&music=0' % AL, wait=2.5)
    b.wait_js("(document.querySelector('.bg.on')||{}).style.backgroundImage.indexOf('al_muza')>=0",
              timeout=20)
    b.shot(OUT)
finally:
    b.close()
print('снимок:', OUT, os.path.getsize(OUT), 'Б')
