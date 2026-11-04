# -*- coding: utf-8 -*-
"""Проверка: строка титр-слоя появляется НА СВОЕЙ ФРАЗЕ (под озвучку), а не сразу.

Реальное время (виртуальное замораживает медиа-часы). Обёртка грузит index.html в iframe,
раз в 250 мс снимает: часы озвучки (voice.currentTime/duration), общий прогресс страницы и
по каждой строке — сколько букв уже показано. Результат POST'ится локальному серверу.

Запуск: python3 _ovl_phrase_probe.py <узел> [секунд]
Проверки:
  1) до `at` у строки 0 букв, после — буквы идут;
  2) строки появляются в порядке `at` (не одновременно);
  3) к концу страницы все буквы на месте.
"""
import glob
import http.server
import json
import os
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
CHROME = glob.glob(os.path.join(WS, '.playwright-browsers', 'chromium*',
                                'chrome-linux*', 'chrome'))[0]
sys.path.insert(0, HERE)
from _vn2_nodes import node_index

NODE = sys.argv[1] if len(sys.argv) > 1 else 's3'
SECS = int(sys.argv[2]) if len(sys.argv) > 2 else 20
WRAP = os.path.join(HERE, 'vn2', '.ovl_probe.html')

data = json.loads(open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8')
                  .read().split('=', 1)[1].strip().rstrip(';'))
ND = [n for n in data['nodes'] if n.get('id') == NODE][0]
OVL = ND['pages'][0].get('ovl') or []
ATS = [it['at'] for it in OVL if 't' in it]
VOD = ND['pages'][0].get('vod') or 0
print('узел %s: at=%s, озвучка %.2f с' % (NODE, ATS, VOD))

ROWS = {}
DONE = threading.Event()
LOCK = threading.Lock()


class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        try:
            rows = json.loads(self.rfile.read(n).decode('utf-8'))
            with LOCK:
                for r in rows:
                    if r and isinstance(r[0], int):
                        ROWS[r[0]] = r
        except Exception:
            pass
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        if self.path.endswith('/done'):
            DONE.set()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def log_message(self, *a):
        pass


s = socket.socket()
s.bind(('127.0.0.1', 0))
PORT = s.getsockname()[1]
s.close()
srv = http.server.HTTPServer(('127.0.0.1', PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

TICKS = SECS * 4
HTML = """<!doctype html><meta charset="utf-8">
<iframe id="f" src="index.html?instant=0&auto=0&text=1&voice=1&music=0&preload=0&node=%d&page=0"
        width="960" height="540"></iframe>
<script>
const POST = "http://127.0.0.1:%d/rows";
const f = document.getElementById("f");
let rows = [], n = 0;
const iv = setInterval(() => {
  const w = f.contentWindow;
  if (!w || !w.document.getElementById("ovl")) return;
  const v = w.document.getElementById("voice");
  const lines = Array.prototype.map.call(w.document.querySelectorAll("#ovl b"), function (b) {
    return b.querySelectorAll("span[data-on]").length + "/" + b.querySelectorAll("span").length;
  });
  rows.push([n, Math.round(performance.now()),
             Math.round((v.currentTime || 0) * 100) / 100,
             Math.round((v.duration || 0) * 100) / 100, v.paused ? 1 : 0, lines]);
  fetch(POST, {method: "POST", body: JSON.stringify(rows)}).catch(() => {});
  n++;
  if (n >= %d) {
    clearInterval(iv);
    fetch(POST, {method: "POST", body: JSON.stringify(rows)})
      .then(() => fetch(POST.replace("/rows", "/done"), {method: "POST", body: "[]"}));
  }
}, 250);
</script>
""" % (node_index(NODE), PORT, TICKS)

with open(WRAP, 'w', encoding='utf-8') as fh:
    fh.write(HTML)

prof = os.path.join(HERE, '.tmp_vo', 'chrome-prof')
p = subprocess.Popen([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                      '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                      '--autoplay-policy=no-user-gesture-required', '--mute-audio',
                      '--user-data-dir=' + prof, '--no-first-run',
                      '--window-size=1280,720', 'file://' + WRAP],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
DONE.wait(timeout=SECS + 25)
time.sleep(0.3)
p.terminate()
try:
    p.wait(timeout=10)
except Exception:
    p.kill()

if not ROWS:
    print('нет данных')
    sys.exit(1)

first_seen = {}
print('%3s %7s %7s %-28s %s' % ('n', 'ms', 'голос', 'строки (показано/всего)', 'прогресс'))
t0 = None
for n in sorted(k for k in ROWS if isinstance(k, int)):
    r = ROWS[n]
    if len(r) < 6:
        continue
    _, ms, t, dur, paused, lines = r
    if t0 is None:
        t0 = ms - t * 1000        # оценка старта озвучки
    # прогресс как его считает движок: часы голоса, иначе длительность записи
    prog = (t / dur) if dur > 0.2 else ((ms - t0) / 1000.0 / VOD if VOD else 0)
    prog = min(1.0, max(0.0, prog))
    print('%3d %7d %7.2f  %-27s %.3f' % (n, ms, t, ' | '.join(lines), prog))
    for i, ln in enumerate(lines):
        shown = int(ln.split('/')[0])
        if shown and i not in first_seen:
            first_seen[i] = (ms, t, prog)

print('\nпервое появление строк:')
bad = 0
for i, (ms, t, prog) in sorted(first_seen.items()):
    at = ATS[i] if i < len(ATS) else 0
    ok = prog + 0.06 >= at
    print('  строка %d: at=%.3f, появилась на прогрессе %.3f (%d мс, голос %.2f с) %s'
          % (i + 1, at, prog, ms, t, 'OK' if ok else 'ПРОБЛЕМА: раньше своей фразы'))
    if not ok:
        bad += 1
last = ROWS[max(k for k in ROWS if isinstance(k, int))][5]
for i, ln in enumerate(last):
    shown, total = ln.split('/')
    if shown != total:
        print('  ПРОБЛЕМА: строка %d не дописана к концу (%s)' % (i + 1, ln))
        bad += 1
print('\nпроблем: %d' % bad)
sys.exit(1 if bad else 0)
