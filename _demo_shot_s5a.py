# -*- coding: utf-8 -*-
"""Скриншот живого демо (Pages): кадр 11 s5a, страница 1 — с титр-слоем."""
import os
import glob
import subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
OUT = os.path.join(HERE, '_sat', 'demo_s5a.png')
URL = ('https://piroman99.github.io/zarynka/vn2/index.html'
       '?instant=1&auto=0&pause=1&pace=0&node=9&page=0&text=1&voice=0&music=0')
subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                '--virtual-time-budget=12000', '--screenshot=' + OUT, URL],
               capture_output=True, text=True, timeout=180)
im = Image.open(OUT).convert('RGB')
print('saved', os.path.relpath(OUT, HERE), im.size)
im.resize((1152, 648), Image.LANCZOS).save(os.path.join(HERE, '_sat', 'demo_s5a_small.png'))
