# -*- coding: utf-8 -*-
"""Есть ли в САМИХ кадрах впечённые надписи (плоские «титровые» цвета)?
Снимаем кадр без титр-слоя и субтитра и ищем пиксели, близкие к CREAM/GOLD/WARM."""
import os
import glob
import subprocess
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
OUT = os.path.join(HERE, '_sat', '_bare')
os.makedirs(OUT, exist_ok=True)
IDX = os.path.join(HERE, 'vn2', 'index.html')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

COLORS = {'cream': (246, 238, 222), 'gold': (255, 210, 120), 'warm': (252, 226, 170)}


def near(px, c, tol=18):
    return all(abs(px[i] - c[i]) <= tol for i in range(3))


for name, page in [('s3', 0), ('s4', 0), ('s5a', 0), ('s5b', 0), ('s1', 0), ('s6', 0),
                   ('s7', 0), ('p6', 0), ('p7', 0), ('p8', 0)]:
    q = ('instant=1&auto=0&pause=1&pace=0&node=%d&page=%d&text=0&voice=0&music=0&ovl=0'
         % (node_index(name), page))
    p = os.path.join(OUT, '%s.png' % name)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--hide-scrollbars', '--window-size=1280,720',
                    '--virtual-time-budget=8000', '--screenshot=' + p,
                    'file://' + IDX + '?' + q],
                   capture_output=True, text=True, timeout=180)
    im = Image.open(p).convert('RGB')
    W, H = im.size
    counts = {}
    for cn, c in COLORS.items():
        n = 0
        for y in range(0, H, 2):
            for x in range(0, W, 2):
                if near(im.getpixel((x, y)), c):
                    n += 1
        counts[cn] = n * 4
    print('%-4s %s' % (name, '  '.join('%s=%d' % kv for kv in counts.items())), flush=True)
