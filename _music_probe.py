# -*- coding: utf-8 -*-
"""Музыка рвётся или нет — замер на РЕАЛЬНОМ времени (виртуальное время Chrome замораживает
медиа-часы, поэтому такой замер ничего не доказывает).

Обёртка грузит index.html в iframe (--allow-file-access-from-files) и раз в 500 мс снимает
`__DBG.music` (+ узел/страницу), а срез POST'ит в локальный http-сервер.

Запуск:  python3 _music_probe.py <start|узел> [preload] [voice] [секунд]
  start — как у игрока: жмём «Начать», дальше листаем кликом по сцене.
  узел  — сразу на кадре (?node=N), тоже с листанием.

Ищем: (1) music.paused стал true, (2) currentTime откатился (трек перезапустился),
(3) шаг времени резко просел (трек «дёрнулся»), (4) трек замолчал, но не на паузе.
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

MODE = sys.argv[1] if len(sys.argv) > 1 else 'start'
PRELOAD = sys.argv[2] if len(sys.argv) > 2 else '1'
VOICE = sys.argv[3] if len(sys.argv) > 3 else '1'
SECS = int(sys.argv[4]) if len(sys.argv) > 4 else 40

base = 'auto=0&text=1&voice=%s&music=1&preload=%s' % (VOICE, PRELOAD)
if MODE != 'start':
    base += '&node=%d&page=0' % node_index(MODE)
WRAP = os.path.join(HERE, 'vn2', '.music_probe.html')

ROWS = {}
DONE = threading.Event()
LOCK = threading.Lock()


class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(n)
        try:
            data = json.loads(body.decode('utf-8'))
            with LOCK:
                for r in data:
                    if r and isinstance(r[0], int):
                        ROWS[r[0]] = r          # обёртка шлёт накопительно — берём последнюю версию
        except Exception as e:
            with LOCK:
                ROWS[-1] = ['ERR', str(e)]
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

TICKS = SECS * 2
HTML = """<!doctype html><meta charset="utf-8">
<iframe id="f" src="index.html?%s" width="960" height="540"></iframe>
<script>
const POST = "http://127.0.0.1:%d/rows";
const f = document.getElementById("f");
const START = %s;
let rows = [], n = 0, started = false;
function send(rs) {
  return fetch(POST, {method: "POST", body: JSON.stringify(rs)}).catch(() => {});
}
const iv = setInterval(() => {
  const w = f.contentWindow;
  if (!w || !w.__DBG) return;
  if (START && !started) {
    const b = w.document.getElementById("start");
    if (b) { b.click(); started = true; }          // «Начать»: значок → посвящение → пролог
  }
  const m = w.__DBG.music, d = w.__DBG;
  rows.push([n, Math.round(performance.now()), Math.round(m.t * 100) / 100,
             m.paused ? 1 : 0, Math.round(m.vol * 100) / 100,
             Math.round((m.dur || 0) * 10) / 10, m.key,
             Math.round(m.duck * 100) / 100, m.src,
             d.node, d.pos, d.inBreak ? 1 : 0]);
  send(rows);
  // листаем, когда музыка уже должна играть (после старта / на кадре — сразу)
  if ((!START || started) && n > 4 && n %% 4 === 0) {
    try { w.document.getElementById("stage").click(); } catch (e) {}
  }
  n++;
  if (n >= %d) {
    clearInterval(iv);
    send(rows).then(() => fetch(POST.replace("/rows", "/done"), {method: "POST", body: "[]"}));
  }
}, 500);
</script>
""" % (base, PORT, 'true' if MODE == 'start' else 'false', TICKS)

with open(WRAP, 'w', encoding='utf-8') as fh:
    fh.write(HTML)

prof = os.path.join(HERE, '.tmp_vo', 'chrome-prof')
p = subprocess.Popen([CHROME, '--headless=new', '--no-sandbox', '--disable-dev-shm-usage',
                      '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                      '--autoplay-policy=no-user-gesture-required', '--mute-audio',
                      '--user-data-dir=' + prof, '--no-first-run',
                      '--window-size=1280,720', 'file://' + WRAP],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
DONE.wait(timeout=SECS + 30)
time.sleep(0.3)
p.terminate()
try:
    p.wait(timeout=10)
except Exception:
    p.kill()

if not ROWS:
    print('нет данных — обёртка не достучалась до приёмника')
    sys.exit(1)

print('режим %s, preload=%s, voice=%s' % (MODE, PRELOAD, VOICE))
print('%3s %7s %8s %6s %5s %6s %-10s %5s %-22s %4s %4s %s' %
      ('n', 'ms', 't', 'paused', 'vol', 'dur', 'key', 'duck', 'src', 'node', 'pos', 'примеч.'))
prev = None
bad = []
for n in sorted(k for k in ROWS if isinstance(k, int)):
    r = ROWS[n]
    if len(r) < 12:
        print(r)
        continue
    _, ms, t, paused, vol, dur, key, duck, src, node, pos, inbreak = r
    mark = ''
    if prev is not None:
        dt = t - prev['t']
        dms = ms - prev['ms']
        if dms > 0:
            expect = dms / 1000.0
            mark = 'Δt=%+.2f/%dмс' % (dt, dms)
            if dt < -0.05:
                mark += ' ОТКАТ'
                bad.append(('откат трека', n, prev['t'], t))
            elif not paused and prev['paused'] is False and dt < 0.5 * expect - 0.2:
                mark += ' ПРОВАЛ'
                bad.append(('провал', n, round(dt, 2), dms))
    if paused and prev is not None and not prev['paused']:
        mark += ' ПАУЗА'
        bad.append(('пауза', n, t))
    if (not paused) and dur > 0 and t == 0 and prev is not None and prev['t'] > 0:
        mark += ' СБРОС В 0'
        bad.append(('сброс в 0', n))
    print('%3d %7d %8.2f %6s %5s %6s %-10s %5s %-22s %4s %4s %s'
          % (n, ms, t, 'да' if paused else 'нет', vol, dur, key, duck,
             (src or '')[:22], node, pos, mark))
    prev = {'t': t, 'ms': ms, 'paused': paused}

print('\nсрезов: %d, проблем: %d' % (len(ROWS), len(bad)))
for b in bad[:15]:
    print('  ', b)
