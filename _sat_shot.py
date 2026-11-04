# -*- coding: utf-8 -*-
"""Рендер кадров-кандидатов ровно в 16:9 (кроп #stage) 1920x1080 + геометрия."""
import os, sys, time, threading, functools, http.server, socketserver
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

OUT = os.path.join(HERE, '_sat')
os.makedirs(OUT, exist_ok=True)

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

GEO = """
(function(){
  var st=document.getElementById('stage').getBoundingClientRect();
  var out=[];
  document.querySelectorAll('.sprite').forEach(function(e){
    if(getComputedStyle(e).opacity==='0') return;
    var b=e.getBoundingClientRect();
    out.push({src:(e.currentSrc||e.src||'').split('/').pop(), top:Math.round(b.top-st.top),
              h:Math.round(b.height), l:Math.round(b.left-st.left), r:Math.round(b.right-st.left)});
  });
  var t=document.getElementById('text'), nm=document.getElementById('name');
  return {stage:{x:Math.round(st.x),y:Math.round(st.y),w:Math.round(st.width),h:Math.round(st.height)},
          sprites:out, who:nm?nm.textContent.trim():'',
          tx:t?t.textContent.trim():''};
})()
"""

CANDS = [
    ('rec03', 'node=10&page=3'),
    ('rec04', 'node=10&page=4'),
    ('rec16', 'node=10&page=16'),
    ('rec34', 'node=10&page=34'),
    ('rec36', 'node=10&page=36'),
    ('rec48', 'node=10&page=48'),
    ('rec50', 'node=10&page=50'),
    ('rec51', 'node=10&page=51'),
    ('star01', 'node=9&page=1'),
    ('s6', 'node=7&page=0'),
    ('s7', 'node=8&page=0'),
    ('s1', 'node=2&page=0'),
]

b = Browser(1920, 1080)
info = {}
try:
    for nm, q in CANDS:
        b.navigate(BASE + '?instant=1&text=1&voice=0&music=0&auto=0&' + q, wait=2.0)
        time.sleep(0.5)
        g = b.js(GEO)
        raw = os.path.join(OUT, '_raw.png')
        b.shot(raw)
        st = g['stage']
        im = Image.open(raw).convert('RGB').crop((st['x'], st['y'], st['x'] + st['w'], st['y'] + st['h']))
        im = im.resize((1920, 1080), Image.LANCZOS)
        im.save(os.path.join(OUT, 'sat_%s.png' % nm))
        info[nm] = g
        print('%-7s %-19s %s' % (nm, g['who'] or '(рассказ)', g['tx'][:80]))
        for s in g['sprites']:
            print('        %-22s top=%4d h=%4d x=%4d..%4d' % (s['src'], s['top'], s['h'], s['l'], s['r']))
finally:
    b.close()
    srv.shutdown()
print('OUT', OUT)
