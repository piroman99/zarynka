# -*- coding: utf-8 -*-
"""Проверка КЛИКА по кнопке «Авто» (а не URL-параметра)."""
import os, re, glob, subprocess, html
HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*', 'chrome-linux*', 'chrome'))[0]

src = open(os.path.join(VN2, 'index.html'), encoding='utf-8').read()
test = src.replace('</body>',
                   '<script>document.getElementById("t-auto").click();</script>\n</body>')
open(os.path.join(VN2, '_t_btn.html'), 'w', encoding='utf-8').write(test)

IDX = 'file://' + os.path.join(VN2, '_t_btn.html')


def dom(q, budget):
    p = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                        '--disable-gpu', '--window-size=1280,720',
                        '--virtual-time-budget=%d' % budget, '--dump-dom', IDX + '?' + q],
                       capture_output=True, text=True, timeout=120)
    return p.stdout


def text_of(d):
    m = re.search(r'<div id="text">(.*?)</div>', d, re.S)
    return html.unescape(m.group(1))[:80] if m else '(нет #text)'


def klass(d):
    m = re.search(r'id="t-auto" class="([^"]*)"', d)
    return m.group(1) if m else '(?)'


q = 'node=9&page=0&instant=1&text=1&voice=0&music=0'
for b in (3000, 12000):
    d = dom(q, b)
    print('t=%ds  t-auto.class=%r  #text=%s' % (b // 1000, klass(d), text_of(d)))
