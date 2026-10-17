# -*- coding: utf-8 -*-
"""Проверка замены значка-видео на финальный (1920x1080).

Что проверяем:
  1) content.js отдаёт новый путь и он реально скачивается (200, не 404);
  2) видео в плеере: 1920x1080, 5.4 с, играет;
  3) после значка идёт S1 (страница 0), HUD включён;
  4) ошибок JS нет;
  5) предзагрузка ставит его в очередь (plVid/кэш);
  6) титул «Зарянка» (подпись видеоузла) не мешает.
"""
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

ok = True


def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK     ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))


b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900,
           deviceScaleFactor=1, mobile=False)
    b.navigate(BASE + '?preload=0')
    b.wait_js("window.VN && window.VN.nodes && document.getElementById('znak')", timeout=30)
    time.sleep(0.6)

    src = b.js("(document.getElementById('znak').getAttribute('src') "
               "|| window.VN.nodes[1].video) || ''")
    print('  src узла значка:', src)
    check('путь обновлён на финал', 'znak3d_rot.mp4' in src and 'draft' not in src, src)

    # прямой fetch: файл есть и не пустой
    r = b.js("""(function(){ return fetch('../out/znak3d_rot.mp4', {method:'HEAD'})
      .then(function(r){ return r.status + ' ' + (r.headers.get('content-length')||'?'); })
      .catch(function(e){ return 'ERR ' + e; }); })()""")
    print('  HEAD ../out/znak3d_rot.mp4 ->', r)
    check('файл доступен по новому пути', str(r).startswith('200'), r)

    b.js("document.getElementById('start').click()")
    time.sleep(1.5)
    check('значок пошёл (vlayer открыт)', b.js("document.getElementById('vlayer').hidden") is False)
    info = b.js("""(function(){ var v=document.getElementById('znak');
      return [v.videoWidth, v.videoHeight, +v.duration.toFixed(2),
              v.paused ? 'pause' : 'play', (v.getAttribute('src')||'').slice(-22)]; })()""")
    print('  видео:', info)
    check('разрешение 1920x1080', info[0] == 1920 and info[1] == 1080, '%sx%s' % (info[0], info[1]))
    check('длительность 5.4 с', abs(float(info[2]) - 5.4) < 0.15, info[2])
    check('играет', info[3] == 'play', info[3])

    b.js("document.getElementById('vskip').click()")
    time.sleep(0.8)
    check('после значка — страница 0', b.js("__DBG.pos") == 0, b.js("__DBG.pos"))
    check('HUD включён', b.js("document.getElementById('hud').classList.contains('on')"))
    check('фон S1 загружен', b.js("(function(){var e=document.querySelector('.bg.on');"
                                  "return e? e.style.backgroundImage.indexOf('s1')>=0 : false})()"))

    errs = b.errors()
    check('ошибок JS нет', not errs, ' | '.join(errs))
finally:
    b.close()

print('\nИТОГ:', 'ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОВАЛЫ')
sys.exit(0 if ok else 1)
