# -*- coding: utf-8 -*-
"""Можно ли запускать озвучку/музыку БЕЗ клика пользователя?

Проверяем политику автозапуска как в обычном браузере (без флага
--autoplay-policy=no-user-gesture-required, который стоит в тестовом _cdp):
зовём play() до любого жеста и смотрим, что вернёт промис.
"""
import os
import sys
import json
import glob
import time
import tempfile
import subprocess
import threading
import functools
import http.server
import socketserver
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WS_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS_ROOT, '.playwright-browsers', 'chromium-*',
                                'chrome-linux64', 'chrome'))[0]
sys.path.insert(0, HERE)
from _cdp import _WS          # noqa: E402


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/vn2/index.html?preload=0' % PORT

prof = tempfile.mkdtemp(prefix='autoplay-')
p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                      '--hide-scrollbars', '--window-size=1280,720',
                      '--user-data-dir=' + prof, '--remote-debugging-port=0',
                      'about:blank'],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
ws_url = None
t0 = time.time()
while time.time() - t0 < 40:
    line = p.stderr.readline()
    if 'DevTools listening on' in line:
        ws_url = line.split('DevTools listening on', 1)[1].strip()
        break
port = ws_url.rsplit(':', 1)[1].split('/')[0]
target = None
for _ in range(60):
    try:
        data = json.load(urllib.request.urlopen('http://127.0.0.1:%s/json/list' % port, timeout=5))
        pages = [t for t in data if t.get('type') == 'page']
        if pages:
            target = pages[0]
            break
    except Exception:
        pass
    time.sleep(0.3)

ws = _WS(target['webSocketDebuggerUrl'])
mid = [0]


def send(method, **params):
    mid[0] += 1
    ws.send({'id': mid[0], 'method': method, 'params': params})
    while True:
        msg = ws.recv()          # _WS.recv уже возвращает разобранный dict
        if msg.get('id') == mid[0]:
            return msg


def js(expr):
    r = send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True)
    return (r.get('result') or {}).get('result', {}).get('value')


send('Runtime.enable')
send('Page.enable')
send('Page.navigate', url=URL)
time.sleep(2.0)

res = js("""(async () => {
  const v = document.getElementById('voice'), m = document.getElementById('music');
  const out = {};
  v.src = 'audio/vo/s1_00.mp3';
  try { await v.play(); out.voice = 'ok'; } catch (e) { out.voice = 'blocked: ' + e.name; }
  m.src = '../assets/audio/sketch/prolog_bed_soft_0.mp3';
  try { await m.play(); out.music = 'ok'; } catch (e) { out.music = 'blocked: ' + e.name; }
  return out;
})()""")
print('автозапуск БЕЗ клика:', res)
ws.close()
p.terminate()
