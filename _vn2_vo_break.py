# -*- coding: utf-8 -*-
"""Проверка двух правок 2026-10-21:
  1) склеенная страница озвучивается ДВУМЯ голосами подряд
     («— Спасибо,» Екатерина → «от улыбки…» закадр) и адрес файла несёт версию ?v=;
  2) переход пролог-крыльцо → кабинет Старика длинный: затемнение → лого → осветление.
Снимки: assets/review/review_115_trans_{dark,logo,light}.png
"""
import os, sys, time, threading, functools, http.server, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser
import _vo_util as U

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT
SHOT = os.path.join(HERE, 'assets', 'review')

ok = True
def check(name, cond, extra=''):
    global ok
    ok = ok and bool(cond)
    print(('  OK   ' if cond else '  ПРОВАЛ ') + name + (' — ' + str(extra) if extra else ''))

NODE = {n.get('id'): i for i, n in enumerate(U.load_content()['nodes'])}
print('узлы:', NODE)

b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900,
           deviceScaleFactor=1, mobile=False)

    # ---------- 1) два голоса на одной странице ----------
    b.navigate(BASE + '?node=%d&page=18&preload=0&instant=1' % NODE['reception'])
    time.sleep(1.2)
    src0 = b.js("(document.getElementById('voice').getAttribute('src')||'')")
    check('страница 18: первый файл = rec_22', 'rec_22.mp3' in src0, src0)
    check('в адресе есть версия озвучки', '?v=' in src0, src0)
    check('текст страницы = реплика + вставка',
          b.js("document.getElementById('text').textContent") ==
          '— Спасибо, — от улыбки вокруг её глаз разбежались морщинки,')
    # ждём перехода на второй сегмент
    got = ''
    t0 = time.time()
    while time.time() - t0 < 12:
        s = b.js("(document.getElementById('voice').getAttribute('src')||'')")
        if 'rec_22b.mp3' in s:
            got = s
            break
        time.sleep(0.2)
    check('после реплики включился второй файл rec_22b', bool(got), got or 'не дождались')
    check('второй сегмент не перебил первый сразу', time.time() - t0 > 0.4,
          '%.1f с' % (time.time() - t0))

    # ---------- 2) длинный переход в кабинет Старика ----------
    # Сначала МЕРЯЕМ без снимков (скриншот по CDP тормозит опрос), потом отдельно снимаем.
    def enter_var2():
        b.navigate(BASE + '?node=%d&preload=0' % NODE['s7'])
        time.sleep(1.2)
        for _ in range(6):            # 1-й клик дописывает печать, 2-й — листает
            b.js("document.getElementById('stage').click()")
            time.sleep(0.25)
            st = b.js("[document.getElementById('trans').classList.contains('on'),"
                      " __DBG.node]")
            if st[0] or st[1] == NODE['starik']:
                return

    enter_var2()
    seen, t0 = {'on': 0, 'logo': 0, 'node': None}, time.time()
    while time.time() - t0 < 5.0:
        st = b.js("[document.getElementById('trans').classList.contains('on'),"
                  " document.getElementById('translogo').classList.contains('on'),"
                  " __DBG.node]")
        el = time.time() - t0
        if st[0]:
            seen['on'] = max(seen['on'], el)
        if st[1]:
            seen['logo'] = max(seen['logo'], el)
        if st[2] == NODE['starik'] and seen['node'] is None:
            seen['node'] = el
        time.sleep(0.06)
    print('  тайминги: затемнение+осветление %.2f с, лого %.2f с, кабинет на %.2f с'
          % (seen['on'], seen['logo'], seen['node'] or -1))
    check('затемнение есть', seen['on'] > 0.5, '%.2f с' % seen['on'])
    check('лого показано в темноте', seen['logo'] > 0.5, '%.2f с' % seen['logo'])
    check('переход дольше 1.5 с', seen['on'] > 1.5, '%.2f с' % seen['on'])
    check('сцена сменилась на кабинет', seen['node'] is not None, seen['node'])
    check('кабинет под тёмным (до осветления)',
          seen['node'] is not None and seen['node'] < seen['on'],
          '%.2f / %.2f' % (seen['node'] or -1, seen['on']))

    # ---------- снимки трёх фаз (отдельный прогон, чтобы не мешать таймингам) ----------
    enter_var2()
    time.sleep(0.25)
    b.shot(os.path.join(SHOT, 'review_115_trans_dark.png'))
    time.sleep(0.9)
    b.shot(os.path.join(SHOT, 'review_115_trans_logo.png'))
    time.sleep(1.6)
    b.shot(os.path.join(SHOT, 'review_115_trans_light.png'))
    check('три кадра сняты',
          all(os.path.exists(os.path.join(SHOT, 'review_115_trans_%s.png' % n))
              for n in ('dark', 'logo', 'light')))

    errs = b.errors()
    check('js-ошибок нет', not errs, errs)
finally:
    b.close()

print('\nИТОГ: ' + ('ВСЁ ЗЕЛЁНОЕ' if ok else 'ЕСТЬ ПРОБЛЕМЫ'))
sys.exit(0 if ok else 1)
