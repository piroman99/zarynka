# -*- coding: utf-8 -*-
"""DOM-дамп титр-слоя ВСЕХ страниц пролога: точная геометрия плашек и строк
(inline-стили, пересчёт в 2400x1350). Плюс проверка: центр строки == центр плашки."""
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
IDX = os.path.join(HERE, 'vn2', 'index.html')
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

E = 2400.0
WANT = [('s3', 0), ('s4', 0), ('s5a', 0), ('s5a', 1), ('s5b', 0)]


def px(v, full=E):
    """значение inline-стиля → пиксели пространства 2400x1350 (%, em от ширины кадра, px)"""
    v = v.strip()
    m = re.match(r'(-?[\d.]+)%', v)
    if m:
        return float(m.group(1)) * full / 100.0
    m = re.match(r'(-?[\d.]+)em', v)
    if m:
        return float(m.group(1)) * E
    m = re.match(r'(-?[\d.]+)px', v)
    if m:
        return float(m.group(1))
    return 0.0


bad = 0
for nid, p in WANT:
    q = ('instant=1&auto=0&pause=1&pace=0&node=%d&page=%d&text=1&voice=0&music=0'
         % (node_index(nid), p))
    r = subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
                        '--disable-dev-shm-usage', '--hide-scrollbars',
                        '--window-size=1280,720', '--virtual-time-budget=6000',
                        '--dump-dom', 'file://' + IDX + '?' + q],
                       capture_output=True, text=True, timeout=180)
    dom = r.stdout
    m = re.search(r'<div id="ovl"[^>]*>(.*?)</div>\s*</div>', dom, re.S)
    inner = m.group(1) if m else ''
    if not inner.strip():
        print('%s стр.%d: ПУСТОЙ #ovl  rc=%s' % (nid, p + 1, r.returncode))
        bad += 1
        continue
    print('\n=== %s стр.%d ===' % (nid, p + 1))
    boxes = []
    for st in re.findall(r'<i style="([^"]*)"></i>', inner):
        d = dict((k.strip(), v.strip()) for k, v in
                 (kv.split(':', 1) for kv in st.split(';') if ':' in kv))
        x0, y0 = px(d.get('left', '0')), px(d.get('top', '0'), 1350.0)
        bx = (x0, x0 + px(d.get('width', '0'), E), y0, y0 + px(d.get('height', '0'), 1350.0))
        boxes.append(bx)
        print('  плашка x %.0f..%.0f y %.0f..%.0f  центр %.1f  bg=%s'
              % (bx[0], bx[1], bx[2], bx[3], (bx[0] + bx[1]) / 2.0,
                 d.get('background', '')))
    # текст теперь набором span'ов (вариант B, 2026-11-04) — берём разметку целиком и снимаем теги
    for st, body in re.findall(r'<b style="([^"]*)">(.*?)</b>', inner, re.S):
        t = re.sub(r'<[^>]+>', '', body)
        d = dict((k.strip(), v.strip()) for k, v in
                 (kv.split(':', 1) for kv in st.split(';') if ':' in kv))
        x, y = px(d.get('left', '0')), px(d.get('top', '0'), 1350.0)
        tf = d.get('transform', '')
        tr = re.search(r'translate\((-?[\d.]+)px,\s*(-?[\d.]+)px\)', tf)
        if tr:
            x += float(tr.group(1))
            y += float(tr.group(2))
        print('  текст %-30r x=%.0f y=%.0f кегль %.0f  сдвиг от центра кадра %+.0f'
              % (t[:28], x, y, px(d.get('font-size', '0')), x - E / 2))
print('\nпустых слоёв: %d' % bad)
sys.exit(1 if bad else 0)
