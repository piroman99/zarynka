# -*- coding: utf-8 -*-
"""Проверка: тот же ли шрифт в браузере, что и в замерах. Рендерим строку чипа
woff2-сабсетом при font-size 100px и меряем реальную ширину по пикселям.
Ожидание: 702/46 = 15.26 em → при 100px должно быть ~1526 px."""
import os
import glob
import subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
SAT = os.path.join(HERE, '_sat')
HTML = os.path.join(SAT, '_fonttest.html')
TXT = 'ДВА МЕСТА — ЛЮДЯМ С УЛИЦЫ'
FONT = os.path.abspath(os.path.join(HERE, 'vn2', 'fonts', 'gothic-demi.woff2'))

open(HTML, 'w', encoding='utf-8').write("""<!doctype html><meta charset="utf-8">
<style>
@font-face{font-family:G;src:url("file://%s") format("woff2");}
body{margin:0;background:#fff}
#a{font-family:G,sans-serif;font-size:100px;white-space:pre;color:#000;line-height:1.4}
</style><div id="a">%s</div>""" % (FONT, TXT))

p = os.path.join(SAT, '_fonttest.png')
subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
                '--disable-dev-shm-usage', '--hide-scrollbars',
                '--window-size=1600,300', '--virtual-time-budget=4000',
                '--screenshot=' + p, 'file://' + HTML],
               capture_output=True, text=True, timeout=120)
im = Image.open(p).convert('RGB')
W, H = im.size
px = im.load()
xs, ys = [], []
for y in range(H):
    for x in range(W):
        r, g, b = px[x, y]
        if r < 128 and g < 128 and b < 128:
            xs.append(x)
            ys.append(y)
if xs:
    print('ink: x %d..%d  ширина %d  (ожидание ~1526 при 100px)' % (min(xs), max(xs),
                                                                    max(xs) - min(xs)))
    print('ink: y %d..%d  высота %d' % (min(ys), max(ys), max(ys) - min(ys)))
else:
    print('текст не отрисовался — шрифт не загрузился?')
print('saved', os.path.relpath(p, HERE))
