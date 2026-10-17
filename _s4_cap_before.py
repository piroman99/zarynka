# -*- coding: utf-8 -*-
"""Снимок «до» (старая плашка S4 из HEAD) для сравнения: подменяем webp, снимаем, возвращаем."""
import os
import shutil
import subprocess
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium-*', 'chrome-linux64', 'chrome'))[0]
WEBP = os.path.join(HERE, 'vn2', 'img', 'prolog', 's4.webp')
BAK = os.path.join(HERE, '.tmp_s4_new.webp')
OUT = os.path.join(HERE, 'assets', 'review', 'review_113_s4_cap_before.png')

shutil.copy2(WEBP, BAK)
try:
    old = subprocess.run(['git', 'show', 'HEAD:vn2/img/prolog/s4.webp'],
                         cwd=HERE, check=True, stdout=subprocess.PIPE).stdout
    open(WEBP, 'wb').write(old)
    print('старый webp:', len(old), 'B')
    url = ('file://' + os.path.join(HERE, 'vn2', 'index.html')
           + '?node=5&text=1&voice=0&music=0&instant=1')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--hide-scrollbars',
                    '--allow-file-access-from-files', '--window-size=1600,900',
                    '--virtual-time-budget=2500', '--screenshot=' + OUT, url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('before ->', os.path.relpath(OUT, HERE), os.path.getsize(OUT), 'B')
finally:
    shutil.copy2(BAK, WEBP)
    os.remove(BAK)
    print('новый webp возвращён:', os.path.getsize(WEBP), 'B')
