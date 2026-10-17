# -*- coding: utf-8 -*-
"""Проверка на МЕДЛЕННОЙ сети (CDP throttling): видна ли полоса, ждёт ли кнопка «Начать».
Снимки: титул в процессе загрузки, титул после, страница S1 сразу после старта.
"""
import os, sys, time, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE))
srv.handle_error = lambda *a: None      # браузер рвёт соединения при закрытии — не шумим
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % port

b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900, deviceScaleFactor=1, mobile=False)
    b.send('Network.enable')
    # ~2 Мбит/с, RTT 150 мс — как средний мобильный интернет
    b.send('Network.emulateNetworkConditions', offline=False, latency=150,
           downloadThroughput=int(2_000_000 / 8), uploadThroughput=int(500_000 / 8),
           connectionType='cellular3g')

    b.navigate(BASE)
    shots = [0.7, 2.0, 4.0, 7.0]
    t0 = time.time()
    prev = 0
    for mark in shots:
        while time.time() - t0 < mark:
            time.sleep(0.05)
        st = b.js("(function(){var e=document.getElementById('pltext'),b=document.getElementById('plbar');"
                  "return (e?e.textContent:'')+' |bar='+(b?b.style.width:'')})()")
        print('t=%.1fs  %s' % (time.time() - t0, st))
        p = os.path.join(HERE, 'assets', 'review', '_pl_slow_%ds.png' % int(round(mark)))
        b.js("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(1))))")
        b.shot(p)

    print('--- жмём «Начать» на медленной сети ---')
    b.js("document.getElementById('start').click()")
    time.sleep(0.3)
    print('  текст кнопки:', b.js("document.getElementById('start').textContent"))
    ok = b.wait_js("!document.getElementById('vlayer').hidden", timeout=60)
    print('  значок пошёл:', ok, '| прошло %.1f с' % (time.time() - t0))
    print('  znak.readyState:', b.js("document.getElementById('znak').readyState"),
          '| readyState 4 = буфер полный, чёрного кадра не будет')
    b.js("document.getElementById('vskip').click()")
    time.sleep(1.2)
    print('  voice.readyState:', b.js("document.getElementById('voice').readyState"))
    print('  фон:', b.js("(function(){var a=document.getElementById('bg-a'),c=document.getElementById('bg-b');return (a.classList.contains('on')?a:c).style.backgroundImage})()"))
    b.js("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(1))))")
    b.shot(os.path.join(HERE, 'assets', 'review', '_pl_slow_s1.png'))
    print('  ошибок JS:', len(b.errors()))
    for e in b.errors()[:6]:
        print('   ', e)
finally:
    b.close()
    srv.shutdown()
    srv.server_close()
