# -*- coding: utf-8 -*-
"""Кадры-проверки: посвящение, титры-ролл (3 положения), экран конца, CG-страница."""
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
  var t=document.getElementById('text'), nm=document.getElementById('name');
  var bg=[].map.call(document.querySelectorAll('.bg.on'),
        function(e){return (getComputedStyle(e).backgroundImage||'').split('/').pop().replace(/["')]/g,'');});
  var sp=[].filter.call(document.querySelectorAll('.sprite'),function(e){return getComputedStyle(e).opacity!=='0';}).length;
  return {stage:{x:Math.round(st.x),y:Math.round(st.y),w:Math.round(st.width),h:Math.round(st.height)},
          who:nm?nm.textContent.trim():'', tx:t?t.textContent.trim():'',
          bg:bg, sprites:sp,
          ded:document.getElementById('ded').classList.contains('show'),
          cr:document.getElementById('credits').classList.contains('show'),
          end:document.getElementById('end').classList.contains('show')};
})()
"""

# остановить ролл на доле пути (только для снимка): ставим transform напрямую,
# потому что у живой анимации нельзя перескочить через animation-delay
PAUSE_ROLL = """
(function(p){
  var l=document.getElementById('crlist'), v=document.getElementById('crview');
  if(!l) return 'no list';
  var h=l.offsetHeight, vh=v.clientHeight;
  l.style.animation='none';
  var y = vh*0.5 - h*p;                  // p = 0 — ролл внизу, p = 1 — ушёл вверх
  l.style.transform='translate(-50%,'+Math.round(y)+'px)';
  return 'h='+h+' vh='+vh+' y='+Math.round(y);
})(__P__)
"""

SHOTS = [
    ('ded',       'node=2&auto=0',                      False, None),
    ('cr_a',      'node=99&credits=1',                  True,  0.06),
    ('cr_b',      'node=99&credits=1',                  True,  0.42),
    ('cr_c',      'node=99&credits=1',                  True,  0.92),
    ('end',       'node=99&instant=1&credits=0',        True,  None),
    ('rec47_cg',  'node=11&page=47',                    False, None),
    ('rec48',     'node=11&page=48',                    False, None),
]

b = Browser(1920, 1080)
try:
    for name, q, full, roll in SHOTS:
        inst = 'instant=1&' if 'instant=1' in q else ''
        url = BASE + '?' + inst + 'text=1&voice=0&music=0&' + q.replace('instant=1', '').strip('&')
        b.navigate(url, wait=2.2)
        time.sleep(0.4)
        if roll is not None:
            print('   roll', b.js(PAUSE_ROLL.replace('__P__', str(roll))))
            time.sleep(0.5)
        g = b.js(GEO)
        raw = os.path.join(OUT, '_raw.png')
        b.shot(raw)
        im = Image.open(raw).convert('RGB')
        if not full:
            st = g['stage']
            im = im.crop((st['x'], st['y'], st['x'] + st['w'], st['y'] + st['h']))
        im.save(os.path.join(OUT, 'new_%s.png' % name))
        print('%-9s bg=%s sprites=%d ded=%s cr=%s end=%s  %s' %
              (name, ','.join(g['bg']), g['sprites'], g['ded'], g['cr'], g['end'], g['tx'][:55]))
finally:
    b.close()
    srv.shutdown()
print('OUT', OUT)
