# -*- coding: utf-8 -*-
import os, sys, time, threading, functools, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from _cdp import Browser

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT

b = Browser(390, 844)
try:
    b.navigate(BASE + '?preload=0')
    b.wait_js("!!window.__DBG", 30)
    time.sleep(1)
    print("innerWidth", b.js("innerWidth"), "clientW", b.js("document.documentElement.clientWidth"))
    print("body scrollW", b.js("document.body.scrollWidth"),
          "doc scrollW", b.js("document.documentElement.scrollWidth"))
    print("body rect", b.js("JSON.stringify(document.body.getBoundingClientRect())"))
    # кто шире вьюпорта?
    print("wide els:", b.js("""(function(){var w=innerWidth,o=[];
      document.querySelectorAll('body *').forEach(function(e){
        var r=e.getBoundingClientRect();
        if (r.right > w+1 && r.width>0) o.push(e.tagName+'#'+(e.id||'')+'.'+(e.className||'')+' r='+Math.round(r.right)+' w='+Math.round(r.width));
      }); return o.slice(0,12);})()"""))
    b.js("document.getElementById('start').click()")
    b.wait_js("document.getElementById('hud').classList.contains('on')", 40)
    time.sleep(1)
    b.js("document.getElementById('t-menu').click()")
    time.sleep(0.4)
    print("tools rect", b.js("JSON.stringify(document.getElementById('tools').getBoundingClientRect())"))
    print("wide els in game:", b.js("""(function(){var w=innerWidth,o=[];
      document.querySelectorAll('body *').forEach(function(e){
        var r=e.getBoundingClientRect();
        if (r.right > w+1 && r.width>0) o.push(e.tagName+'#'+(e.id||'')+' r='+Math.round(r.right)+' w='+Math.round(r.width));
      }); return o.slice(0,12);})()"""))
finally:
    b.close(); srv.shutdown()
