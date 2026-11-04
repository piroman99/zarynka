# -*- coding: utf-8 -*-
"""Диагностика: применяется ли crTwinkle (prefers-reduced-motion? каскад?)."""
import os, sys, time, threading, functools, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

Q = """
(function(){
  var out={};
  out.rm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  out.sheets = [].map.call(document.styleSheets, function(s){return (s.href||'inline').split('/').pop();});
  var found=[];
  [].forEach.call(document.styleSheets, function(s){
    var rules; try{ rules=s.cssRules; }catch(e){ return; }
    [].forEach.call(rules, function(r){
      if(r.cssText && r.cssText.indexOf('crTwinkle')>=0) found.push(r.cssText.slice(0,160));
      if(r.cssText && r.cssText.indexOf('cr-stars')>=0) found.push('STARS:'+r.cssText.slice(0,80));
    });
  });
  out.found=found;
  var e=document.querySelector('.cr-stars .l0');
  out.anim = e? getComputedStyle(e).animationName : 'no-el';
  out.dur  = e? getComputedStyle(e).animationDuration : '-';
  out.op   = e? getComputedStyle(e).opacity : '-';
  out.hidden = document.getElementById('credits').classList.contains('show');
  return out;
})()
"""

b = Browser(1920, 1080)
try:
    b.navigate(BASE + '?node=99&credits=1&text=1&voice=0&music=0', wait=2.2)
    time.sleep(0.3)
    g = b.js(Q)
    print('reduced-motion:', g['rm'])
    print('таблицы стилей:', g['sheets'])
    print('правила про звёзды:', len(g['found']))
    for f in g['found'][:6]:
        print('   ', f)
    print('anim=', g['anim'], 'dur=', g['dur'], 'op=', g['op'], 'credits.show=', g['hidden'])
finally:
    b.close()
    srv.shutdown()
