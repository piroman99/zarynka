# -*- coding: utf-8 -*-
"""Финальная регрессия движка после предзагрузки:
  1) быстрая сеть: предзагрузка доходит до 100 %, листание = 0 запросов;
  2) медленная сеть: кнопка «Начать» уходит в «Загрузка…», ВТОРОЙ клик стартует сразу;
  3) ?preload=0 — предзагрузки нет вообще (ни одного лишнего запроса).
"""
import os, sys, time, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

REQ = []
LOCK = threading.Lock()


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        with LOCK:
            REQ.append(self.path)
        return super().do_GET()


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % port

ok = True


def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK   ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))


b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900, deviceScaleFactor=1, mobile=False)

    print('1) быстрая сеть')
    b.navigate(BASE)
    done = b.wait_js("(function(){var e=document.getElementById('pl');return !!(e&&e.classList.contains('done'))})()", timeout=90)
    check('предзагрузка завершилась', done)
    check('изображений в кэше 12', b.js("__PL.img.size") == 12, b.js("__PL.img.size"))
    check('аудио в кэше 65', b.js("__PL.aud.size") == 65, b.js("__PL.aud.size"))
    check('видео в кэше 2', b.js("__PL.vid.size") == 2, b.js("__PL.vid.size"))
    check('промахов (404) нет', b.js("__PL.miss.size") == 0, b.js("__PL.miss.size"))

    b.js("document.getElementById('start').click()")
    b.wait_js("!document.getElementById('vlayer').hidden", timeout=30)
    b.js("document.getElementById('vskip').click()")
    time.sleep(0.6)
    with LOCK:
        REQ.clear()
    last = -1
    for i in range(30):
        b.js("document.getElementById('next').click()")
        time.sleep(0.25)
    last = b.js("__DBG.pos")
    with LOCK:
        during = list(REQ)
    check('листание 30 кликов = 0 сетевых запросов', len(during) == 0, during[:5])
    check('позиция уехала вперёд', last > 0, 'pos=' + str(last))
    check('голос играет из blob', str(b.js("document.getElementById('voice').getAttribute('src')")).startswith('blob:'))

    print('2) медленная сеть + повторный клик')
    b.send('Network.enable')
    b.send('Network.clearBrowserCache')      # иначе ассеты возьмутся из кэша 1-го прогона
    b.send('Network.emulateNetworkConditions', offline=False, latency=150,
           downloadThroughput=250000, uploadThroughput=62500, connectionType='cellular3g')
    b.navigate('about:blank')
    time.sleep(0.5)
    b.navigate(BASE)
    time.sleep(3)
    b.js("document.getElementById('start').click()")
    time.sleep(0.4)
    check('кнопка ушла в «Загрузка…»', 'Загрузка' in str(b.js("document.getElementById('start').textContent")),
          b.js("document.getElementById('start').textContent"))
    t = time.time()
    b.js("document.getElementById('start').click()")     # второй клик = старт сразу
    started = b.wait_js("!document.getElementById('vlayer').hidden", timeout=20)
    check('второй клик стартует без ожидания', started, '%.1f с' % (time.time() - t))
    check('кнопка вернулась в «Начать»', b.js("document.getElementById('start').textContent") == 'Начать',
          b.js("document.getElementById('start').textContent"))

    print('3) ?preload=0')
    b.send('Network.emulateNetworkConditions', offline=False, latency=0,
           downloadThroughput=-1, uploadThroughput=-1, connectionType='none')
    with LOCK:
        REQ.clear()
    b.navigate(BASE + '?preload=0')
    time.sleep(2.5)
    with LOCK:
        REQ.clear()                      # отсекаем ещё летящие запросы прошлой страницы
    time.sleep(4)
    with LOCK:
        r = list(REQ)
    media = [q for q in r if (q.startswith('/vn2/img/') and 'logo' not in q)
             or q.startswith('/vn2/audio/') or q.startswith('/assets/audio')]
    check('при ?preload=0 медиа не качается', len(media) == 0, media[:5])
    check('кнопка сразу «Начать»', b.js("document.getElementById('start').textContent") == 'Начать',
          b.js("document.getElementById('start').textContent"))

    print('ошибок JS за весь тест:', len(b.errors()))
    for e in b.errors()[:6]:
        print('   ', e)
finally:
    b.close()
    srv.shutdown()
    srv.server_close()

print('\nИТОГ:', 'всё зелёное' if ok else 'ЕСТЬ ПРОВАЛЫ')
