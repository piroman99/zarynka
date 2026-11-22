# -*- coding: utf-8 -*-
"""ЗАМЕР: где на экране сцена, скамейка и поэт в сцене «аллея» (1600x900).

Печатает геометрию в пикселях сцены и в «сантиметрах» по масштабу скамейки
(высота пропа 59 % сцены ↔ реальная скамейка со спинкой ≈ 90 см).
"""
import os
import sys
import time
import json
import threading
import functools
import http.server
import socketserver

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser
from _vn2_nodes import node_index

N = node_index('alley')
print('узел alley = node %d' % N)

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

JS = r"""
(function(){
  function r(e){ if(!e) return null; var b=e.getBoundingClientRect();
    return {x:Math.round(b.left),y:Math.round(b.top),w:Math.round(b.width),h:Math.round(b.height)}; }
  var stage=document.getElementById('stage');
  var prop=document.querySelector('#props .prop');
  var sp=document.querySelectorAll('#cast .sprite');
  return {
    stage:r(stage), prop:r(prop), propOn: prop? prop.classList.contains('on'):null,
    propSrc: prop? (prop.getAttribute('src')||''):'',
    poet:r(sp[0]), poetOn: sp[0].classList.contains('on'), poetSeated: sp[0].classList.contains('seated'),
    poetSrc: sp[0].getAttribute('src'),
    poetNat:[sp[0].naturalWidth, sp[0].naturalHeight],
    kate:r(sp[1]), kateOn: sp[1].classList.contains('on'),
    win:[innerWidth, innerHeight]
  };
})()
"""

b = Browser(1600, 900)
try:
    b.navigate(BASE + '?node=%d&page=0&instant=1&text=1&voice=0&music=0&auto=0' % N)
    time.sleep(2.0)
    d = b.js(JS)
    print(json.dumps(d, ensure_ascii=False, indent=1))

    st = d['stage']
    print('\n--- сцена %dx%d ---' % (st['w'], st['h']))
    if d['prop']:
        p = d['prop']
        print('скамейка-проп: %dx%d, x %d..%d, y %d..%d' % (p['w'], p['h'], p['x'], p['x'] + p['w'],
                                                            p['y'], p['y'] + p['h']))
        print('  высота пропа = %.1f%% сцены' % (100.0 * p['h'] / st['h']))
        px_per_m = p['h'] / 0.90
        print('  масштаб по скамейке (90 см со спинкой): %.0f px/м' % px_per_m)
        if d['poet']:
            q = d['poet']
            print('  поэт (холст спрайта): %dx%d, высота %.1f%% сцены'
                  % (q['w'], q['h'], 100.0 * q['h'] / st['h']))
            print('  в «сантиметрах» холст поэта = %.0f см; фигура внутри холста 70-88%%'
                  % (100.0 * q['h'] / px_per_m))
            print('  → фигура поэта ≈ %.0f..%.0f см'
                  % (100.0 * q['h'] / px_per_m * 0.70, 100.0 * q['h'] / px_per_m * 0.88))
            print('  нужно (сидящий мужчина ~132 см): %.0f px = %.1f%% сцены на ХОЛСТ'
                  % (1.32 * px_per_m, 100.0 * 1.32 * px_per_m / st['h'] / 0.83))
    b.shot(os.path.join(ROOT, '_sat', 'alley_now.png'))
finally:
    b.close()
print('\nскриншот: _sat/alley_now.png')
