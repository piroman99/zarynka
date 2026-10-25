# -*- coding: utf-8 -*-
"""Снимки титров со звёздами: три положения ролла + замер мерцания."""
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

PAUSE_ROLL = """
(function(p){
  var l=document.getElementById('crlist'), v=document.getElementById('crview');
  var h=l.offsetHeight, vh=v.clientHeight;
  l.style.animation='none';
  var y = vh*0.5 - h*p;
  l.style.transform='translate(-50%,'+Math.round(y)+'px)';
  return 'h='+h+' vh='+vh;
})(__P__)
"""

STAR_PROBE = """
(function(){
  var st=document.querySelector('.cr-stars');
  if(!st) return {ok:false};
  var l=[].map.call(st.children, function(e){
     var cs=getComputedStyle(e);
     return {cls:e.className, op:cs.opacity, anim:cs.animationName, dur:cs.animationDuration,
             bg:(cs.backgroundImage||'').slice(0,40), dots:(cs.backgroundImage.match(/radial-gradient/g)||[]).length};
  });
  return {ok:true, n:l.length, z:getComputedStyle(st).zIndex, layers:l};
})()
"""

b = Browser(1920, 1080)
try:
    for name, pos in (('stars_lo', 0.03), ('stars_mid', 0.45), ('stars_hi', 0.9)):
        b.navigate(BASE + '?node=99&credits=1&text=1&voice=0&music=0&instant=1', wait=2.0)
        time.sleep(0.3)
        print(b.js(PAUSE_ROLL.replace('__P__', str(pos))))
        time.sleep(0.4)
        raw = os.path.join(OUT, '_raw.png')
        b.shot(raw)
        Image.open(raw).convert('RGB').save(os.path.join(OUT, 'cr_%s.png' % name))
        print(name, 'ok')
    # два замера подряд — мерцание реально живое (opacity меняется)
    b.navigate(BASE + '?node=99&credits=1&text=1&voice=0&music=0&instant=1', wait=2.0)
    p = b.js(STAR_PROBE)
    print('слой звёзд:', p['n'], 'z-index', p['z'])
    for l in p['layers']:
        print('  ', l['cls'], 'anim=', l['anim'], 'dur=', l['dur'], 'dots=', l['dots'], 'op=', l['op'])
    o1 = [l['op'] for l in b.js(STAR_PROBE)['layers']]
    time.sleep(1.1)
    o2 = [l['op'] for l in b.js(STAR_PROBE)['layers']]
    print('opacity t0 =', o1)
    print('opacity t1 =', o2)
    print('мерцание живое:', o1 != o2)
finally:
    b.close()
    srv.shutdown()
print('OUT', OUT)
