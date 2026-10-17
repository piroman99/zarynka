# -*- coding: utf-8 -*-
"""Сверка «до/после WebP» на РЕНДЕРЕ: снимаем узлы S5 и Приёмную, сравниваем с PNG-версией."""
import os, sys, shutil, time, threading, functools, http.server, socketserver
import numpy as np
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

REV = os.path.join(HERE, 'assets', 'review')
# сохраняем PNG-версию как эталон, если ещё есть
ref = os.path.join(REV, 'review_96_s5_vn_ok.png')
ref_copy = os.path.join(REV, '_ref_s5_png.png')
if os.path.exists(ref) and not os.path.exists(ref_copy):
    shutil.copy2(ref, ref_copy)
    print('эталон PNG сохранён')

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE))
srv.handle_error = lambda *a: None
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % port

NODE = {'s1': 2, 's2': 3, 's3': 4, 's4': 5, 's5': 6, 's6': 7, 's7': 8, 'reception': 9}

b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900, deviceScaleFactor=1, mobile=False)
    for name in ('s5', 'reception'):
        b.navigate('%s?node=%d&instant=1&text=1&voice=0&music=0' % (BASE, NODE[name]))
        b.wait_js("!!document.querySelector('#text') && document.querySelector('#text').textContent.length > 0", timeout=25)
        time.sleep(1.0)
        p = os.path.join(REV, 'review_96_s5_vn_ok.png' if name == 's5' else '_webp_reception.png')
        b.shot(p)
        print(name, '->', os.path.basename(p), os.path.getsize(p), 'B')
    print('ошибок JS:', len(b.errors()))
    for e in b.errors()[:5]:
        print('  ', e)
finally:
    b.close()
    srv.shutdown()
    srv.server_close()

# сравнение S5: PNG-эталон vs WebP-рендер
if os.path.exists(ref_copy):
    a = Image.open(ref_copy).convert('RGB')
    c = Image.open(os.path.join(REV, 'review_96_s5_vn_ok.png')).convert('RGB')
    if a.size != c.size:
        c = c.resize(a.size)
    d = np.asarray(ImageChops.difference(a, c), np.float32)
    print('S5 рендер: MAE %.3f из 255, макс %d — %s'
          % (d.mean(), d.max(), 'идентично на глаз' if d.mean() < 1.5 else 'ЕСТЬ РАЗЛИЧИЯ'))
