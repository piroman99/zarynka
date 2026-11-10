# -*- coding: utf-8 -*-
"""Проверка сцены «аллея» после правок: звук, проп, шесть эмоций поэта, посадка.

Живой движок + HTTP-статусы всех ресурсов узла (музыка, фон, проп, спрайты).
Печатает геометрию в пикселях и «сантиметрах» (масштаб по Екатерине) и итог OK/FAIL.
"""
import os
import sys
import time
import json
import threading
import functools
import http.server
import socketserver
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser
from _vn2_nodes import node_index

N = node_index('alley')
FILL, BOTTOM_PAD, HIP = 0.85, 0.01, 0.346
# доля высоты картинки пропа НИЖЕ земли у ближнего торца (под ножкой штрих/тень):
# в файле prop_bench.png земля на y=860 из 986, низ маски y=978 -> (978-860)/986
PROP_GROUND_FRAC = (978.0 - 860.0) / 986.0


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/' % PORT

fails = []


def check_http(rel):
    try:
        r = urllib.request.urlopen(BASE + rel, timeout=20)
        n = len(r.read())
        print('  %-46s %d %8d Б' % (rel, r.status, n))
        if r.status != 200 or n < 1000:
            fails.append('%s: %d/%d Б' % (rel, r.status, n))
    except Exception as e:  # noqa: BLE001
        print('  %-46s ОШИБКА %s' % (rel, e))
        fails.append('%s: %s' % (rel, e))


print('--- ресурсы узла alley ---')
for rel in ['vn2/content.js',
            'assets/audio/sketch/alley2_mix.mp3',
            'vn2/img/bg/alley.webp',
            'vn2/img/prop/bench.webp'] + \
        ['vn2/img/char/poet_seat%s.webp' % ('' if e == 'neutral' else '_' + e) for e in
         ('neutral', 'interested', 'upset', 'shy', 'sullen', 'smile')]:
    check_http(rel)

b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900,
           deviceScaleFactor=1, mobile=False)
    b.navigate(BASE + 'vn2/index.html?node=%d&page=0&instant=1&text=1&voice=0&music=1'
                      '&auto=0&preload=0' % N)
    time.sleep(2.5)
    d = b.js("""(function(){
      function r(e){ if(!e) return null; var b=e.getBoundingClientRect();
        return {x:Math.round(b.left),y:Math.round(b.top),
                w:Math.round(b.width),h:Math.round(b.height)}; }
      var st=document.getElementById('stage').getBoundingClientRect();
      var pr=document.querySelector('#props .prop');
      var sp=document.querySelectorAll('#cast .sprite')[0];
      var mu=document.getElementById('music');
      return {stage:{w:st.width,h:st.height},
              prop:r(pr), propSrc:pr.getAttribute('src'),
              poet:r(sp), poetOn:sp.classList.contains('on'),
              poetSrc:sp.getAttribute('src'),
              music:mu? mu.currentSrc||mu.src : null,
              musicReady:mu? mu.readyState : null,
              musicErr:mu? (mu.error? mu.error.code : null) : null};})()""")
    print('\n--- геометрия ---')
    print(json.dumps({k: d[k] for k in ('stage', 'prop', 'poet', 'propSrc', 'poetSrc',
                                        'music', 'musicReady', 'musicErr')},
                     ensure_ascii=False, indent=1))
    if 'alley2_mix' not in (d['music'] or ''):
        fails.append('музыка не alley2_mix: %s' % d['music'])
    if d['musicErr']:
        fails.append('ошибка загрузки музыки: %s' % d['musicErr'])
    if d['propSrc'] != 'img/prop/bench.webp':
        fails.append('проп не тот: %s' % d['propSrc'])
    if not d['poetOn']:
        fails.append('поэт не включён')

    st, pg, pr = d['stage'], d['poet'], d['prop']
    ppm = 738.0 / 1.70 * st['h'] / 757.0
    canvas = pg['h']
    fig = FILL * canvas
    feet = pg['y'] + pg['h'] - BOTTOM_PAD * canvas
    hip = feet - HIP * fig
    seat = pr['y'] + pr['h'] - PROP_GROUND_FRAC * pr['h'] - 0.45 * ppm
    print('\nмасштаб %.1f px/м | фигура поэта %.0f px = %.2f м сидя | холст %.0f px (%.1f%% сцены)'
          % (ppm, fig, fig / ppm, canvas, 100.0 * canvas / st['h']))
    print('ступни %.0f, бёдра %.0f, сиденье пропа %.0f -> разница %+.0f px (%+.1f см)'
          % (feet, hip, seat, seat - hip, (seat - hip) / ppm * 100))
    print('проп: %dx%d, x %d..%d, y %d..%d (%.0f%% сцены по высоте)'
          % (pr['w'], pr['h'], pr['x'], pr['x'] + pr['w'], pr['y'], pr['y'] + pr['h'],
             100.0 * pr['h'] / st['h']))
    if abs(seat - hip) > 12:
        fails.append('сиденье не под бёдрами: %+.0f px' % (seat - hip))

    # шесть эмоций: у всех один масштаб и одна линия бёдер
    print('\n--- шесть эмоций поэта ---')
    for emo in ('upset', 'neutral', 'interested', 'shy', 'sullen', 'smile'):
        f = 'poet_seat' if emo == 'neutral' else 'poet_seat_' + emo
        b.js("""(function(){var e=document.querySelectorAll('#cast .sprite')[0];
          e.src='img/char/%s.webp';})()""" % f)
        time.sleep(0.7)
        q = b.js("""(function(){var e=document.querySelectorAll('#cast .sprite')[0];
          var r=e.getBoundingClientRect();
          return {w:Math.round(r.width),h:Math.round(r.height),nat:e.naturalWidth+'x'+e.naturalHeight,
                  ok:e.complete&&e.naturalWidth>0};})()""")
        print('  %-11s холст %dx%d (натур. %s) %s'
              % (emo, q['w'], q['h'], q['nat'], 'ok' if q['ok'] else 'НЕ ЗАГРУЗИЛСЯ'))
        if not q['ok']:
            fails.append('спрайт %s не загрузился' % emo)
finally:
    b.close()

print('\nИТОГ: ' + ('ВСЁ ЗЕЛЁНОЕ' if not fails else 'FAIL: ' + '; '.join(fails)))
sys.exit(0 if not fails else 1)
