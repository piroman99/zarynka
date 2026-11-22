# -*- coding: utf-8 -*-
"""ЗАМЕР «аллеи» в живом движке: (1) где нарисованная в фоне скамейка, (2) что кроет
проп-скамейка, (3) какой стороной она повёрнута, (4) сколько «сантиметров» в поэте.

Ничего не рисуем на глаз: снимаем два кадра (проп скрыт / показан), ищем в кадре
пятна «дерева» и печатаем координаты в пикселях страницы и в % кадра.
"""
import os
import sys
import time
import json
import base64
import threading
import functools
import http.server
import socketserver

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser
from _vn2_nodes import node_index

N = node_index('alley')
SAT = os.path.join(ROOT, '_sat')
os.makedirs(SAT, exist_ok=True)


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = ('http://127.0.0.1:%d/vn2/index.html?node=%d&page=0&instant=1&text=1&voice=0'
       '&music=0&auto=0' % (PORT, N))

GEOM = r"""
(function(){
  function r(e){ if(!e) return null; var b=e.getBoundingClientRect();
    return {x:Math.round(b.left),y:Math.round(b.top),w:Math.round(b.width),h:Math.round(b.height)}; }
  var st=document.getElementById('stage');
  var pr=document.querySelector('#props .prop');
  var sp=document.querySelectorAll('#cast .sprite')[0];
  return {stage:r(st), prop:r(pr), propOn:pr.classList.contains('on'),
          propSrc:pr.getAttribute('src'),
          poet:r(sp), poetOn:sp.classList.contains('on'),
          poetNat:[sp.naturalWidth,sp.naturalHeight],
          win:[innerWidth,innerHeight]};
})()
"""


def shot(b, path, clip):
    r = b.send('Page.captureScreenshot', format='png',
               clip={'x': clip['x'], 'y': clip['y'], 'width': clip['w'],
                     'height': clip['h'], 'scale': 1})
    open(path, 'wb').write(base64.b64decode(r['data']))
    return path


def wood_blobs(path, x0f=0.0, x1f=0.55, y0f=0.45, y1f=1.0, min_frac=0.0015):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    x0, x1 = int(x0f * W), int(x1f * W)
    y0, y1 = int(y0f * H), int(y1f * H)
    sub = im.crop((x0, y0, x1, y1))
    hsv = np.asarray(sub.convert('HSV')).astype(np.int16)
    Hc, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = (Hc >= 6) & (Hc <= 32) & (S >= 55) & (V >= 45) & (V <= 210)
    # разметка связных пятен на сетке 1:4
    sm = m[::4, ::4]
    lab = np.zeros(sm.shape, np.int32)
    comps = []
    cur = 0
    for yy in range(sm.shape[0]):
        for xx in range(sm.shape[1]):
            if sm[yy, xx] and lab[yy, xx] == 0:
                cur += 1
                st = [(yy, xx)]
                lab[yy, xx] = cur
                pts = []
                while st:
                    a, b2 = st.pop()
                    pts.append((a, b2))
                    for da in (-1, 0, 1):
                        for db in (-1, 0, 1):
                            na, nb = a + da, b2 + db
                            if 0 <= na < sm.shape[0] and 0 <= nb < sm.shape[1] \
                                    and sm[na, nb] and lab[na, nb] == 0:
                                lab[na, nb] = cur
                                st.append((na, nb))
                comps.append(pts)
    comps.sort(key=len, reverse=True)
    out = []
    total = sm.size
    for pts in comps:
        if len(pts) < max(20, min_frac * total):
            break
        ys = [p[0] for p in pts]
        xs = [p[1] for p in pts]
        out.append({'n': len(pts),
                    'x0': x0 + min(xs) * 4, 'x1': x0 + max(xs) * 4,
                    'y0': y0 + min(ys) * 4, 'y1': y0 + max(ys) * 4})
    return out, (W, H)


b = Browser(1600, 900)
try:
    b.navigate(URL)
    time.sleep(2.2)
    g = b.js(GEOM)
    print('геометрия:', json.dumps(g, ensure_ascii=False))
    st = g['stage']
    clip = {'x': st['x'], 'y': st['y'], 'w': st['w'], 'h': st['h']}

    # 1) кадр без пропа
    b.js("document.querySelector('#props .prop').classList.remove('on')")
    time.sleep(0.5)
    p_off = shot(b, os.path.join(SAT, 'probe_noprop.png'), clip)
    # 2) кадр с пропом
    b.js("document.querySelector('#props .prop').classList.add('on')")
    time.sleep(0.5)
    p_on = shot(b, os.path.join(SAT, 'probe_prop.png'), clip)

    off, size = wood_blobs(p_off)
    print('\n--- пятна «дерева» БЕЗ пропа (в пикселях СЦЕНЫ %dx%d) ---' % size)
    for d in off[:8]:
        print('  точек %5d  x %4d..%4d (%.1f..%.1f%%)  y %4d..%4d (%.1f..%.1f%%)'
              % (d['n'], d['x0'], d['x1'], 100.0 * d['x0'] / size[0],
                 100.0 * d['x1'] / size[0], d['y0'], d['y1'],
                 100.0 * d['y0'] / size[1], 100.0 * d['y1'] / size[1]))

    on, _ = wood_blobs(p_on)
    print('\n--- пятна «дерева» С пропом ---')
    for d in on[:8]:
        print('  точек %5d  x %4d..%4d (%.1f..%.1f%%)  y %4d..%4d (%.1f..%.1f%%)'
              % (d['n'], d['x0'], d['x1'], 100.0 * d['x0'] / size[0],
                 100.0 * d['x1'] / size[0], d['y0'], d['y1'],
                 100.0 * d['y0'] / size[1], 100.0 * d['y1'] / size[1]))

    # 3) контур пропа: где он реально лежит (по разнице кадров)
    a = np.asarray(Image.open(p_off).convert('RGB')).astype(np.int16)
    c = np.asarray(Image.open(p_on).convert('RGB')).astype(np.int16)
    diff = np.abs(a - c).sum(2) > 18
    ys, xs = np.nonzero(diff)
    if len(xs):
        print('\nпроп занимает: x %d..%d (%.1f..%.1f%%)  y %d..%d (%.1f..%.1f%%)'
              % (xs.min(), xs.max(), 100.0 * xs.min() / size[0], 100.0 * xs.max() / size[0],
                 ys.min(), ys.max(), 100.0 * ys.min() / size[1], 100.0 * ys.max() / size[1]))
        # сколько нарисованного «дерева» видно ВНЕ пропа
        left = np.zeros_like(diff)
        left[:] = False
        print('площадь пропа: %.1f%% кадра' % (100.0 * diff.mean()))

    # 4) поэт: рост в пикселях и «сантиметрах»
    pg = g['poet']
    print('\nпоэт-спрайт: %dx%d px на странице, натуральный %s, низ %d'
          % (pg['w'], pg['h'], g['poetNat'], pg['y'] + pg['h']))
    print('проп: %s' % json.dumps(g['prop']))
except Exception as e:
    print('ОШИБКА:', type(e).__name__, e)
finally:
    b.close()
