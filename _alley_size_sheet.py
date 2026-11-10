# -*- coding: utf-8 -*-
"""ЛИСТ ДЛЯ ИВАНА: поэт на скамейке в трёх размерах (1.30 / 1.40 / 1.50 м сидя).

Снимается ЖИВЫМ движком (headless Chromium, окно 1600x900 -> сцена 1346x757,
узел alley, стр. 1 «лицо в ладонях»). Скамейка в каждом кадре пересчитана под размер
поэта по формулам `_alley_layout.py`: у ближнего торца спинка 0.90 м, сиденье 0.45 м,
земля = ступни поэта. Всё считается в ДОЛЯХ СЦЕНЫ, поэтому размер окна не влияет.

Выход: _sat/alley_size_sheet.png (+ кадры alley_sz_*.png)
"""
import os
import sys
import json
import time
import threading
import functools
import http.server
import socketserver
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser
from _vn2_nodes import node_index

N = node_index('alley')
SAT = os.path.join(HERE, '_sat')
os.makedirs(SAT, exist_ok=True)

FILL = 0.85                 # фигура / холст спрайта
BOTTOM_PAD = 0.01
HIP = 0.346                 # посадка / высота сидящей фигуры
BENCH_TOP_M = 0.90
BENCH_SEAT_M = 0.45
PROP_NAT = (1303.0, 986.0)
PROP_NEAR_H = 703.0            # высота ближнего торца в пикселях пропа (замер _alley_layout.py)
PROP_GROUND_FRAC = (978.0 - 860.0) / 986.0   # насколько низ картинки ниже земли
SLOT0 = 0.27
ALONG = 0.25
PX_PER_M_AT_757 = 738.0 / 1.70


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = ('http://127.0.0.1:%d/vn2/index.html?node=%d&page=0&instant=1&text=0&voice=0'
       '&music=0&auto=0&preload=0' % (PORT, N))


def shot(b, path, clip=None):
    kw = {'format': 'png'}
    if clip:
        kw['clip'] = {'x': clip[0], 'y': clip[1], 'width': clip[2], 'height': clip[3],
                      'scale': 1}
    r = b.send('Page.captureScreenshot', **kw)
    open(path, 'wb').write(base64.b64decode(r['data']))
    return path


GEOM_JS = """(function(){
  var st=document.getElementById('stage').getBoundingClientRect();
  return {w:st.width,h:st.height,x:st.left,y:st.top};
})()"""

APPLY = """(function(g){
  var sp=document.querySelectorAll('#cast .sprite')[0];
  sp.style.height=g.h+'%';
  var pr=document.querySelector('#props .prop');
  pr.style.height=g.ph+'%'; pr.style.bottom=g.pb+'%'; pr.style.left=g.pl+'%';
  var st=document.getElementById('stage').getBoundingClientRect();
  var s=sp.getBoundingClientRect(), p=pr.getBoundingClientRect();
  return {spriteH:s.height, spriteTop:s.top, spriteBottom:s.bottom,
          propH:p.height, propTop:p.top, propBottom:p.bottom,
          stageH:st.height, stageX:st.left, stageW:st.width};
})()"""

variants = [1.30, 1.40, 1.50]
rows = []
b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900,
           deviceScaleFactor=1, mobile=False)
    b.navigate(URL)
    time.sleep(2.2)
    st = b.js(GEOM_JS)
    ppm = PX_PER_M_AT_757 * st['h'] / 757.0
    print('сцена %.0fx%.0f (x=%.0f), масштаб %.1f px/м' % (st['w'], st['h'], st['x'], ppm))

    for m in variants:
        fig = m * ppm
        canvas = fig / FILL
        h_pct = 100.0 * canvas / st['h']
        feet = st['h'] * (1 + 0.03) - BOTTOM_PAD * canvas
        hip = feet - HIP * fig
        s = BENCH_TOP_M * ppm / PROP_NEAR_H
        prop_h = PROP_NAT[1] * s
        prop_w = PROP_NAT[0] * s
        seat_px = BENCH_SEAT_M * ppm
        # скамейку в каждом варианте ставим так, чтобы сиденье было ровно под бёдрами
        bottom_pct = -100.0 * (hip + seat_px + PROP_GROUND_FRAC * prop_h - st['h']) / st['h']
        x_along = (8.0 + ALONG * (1194.0 - 8.0)) * s
        left_pct = 100.0 * (SLOT0 * st['w'] - x_along + prop_w / 2.0) / st['w']
        g = {'h': round(h_pct, 2), 'ph': round(100.0 * prop_h / st['h'], 2),
             'pb': round(bottom_pct, 2), 'pl': round(left_pct, 2)}
        js = json.dumps(g)
        info = b.js("""(function(g){
          var sp=document.querySelectorAll('#cast .sprite')[0];
          sp.style.height=g.h+'%';
          var pr=document.querySelector('#props .prop');
          pr.style.height=g.ph+'%'; pr.style.bottom=g.pb+'%'; pr.style.left=g.pl+'%';
          var st=document.getElementById('stage').getBoundingClientRect();
          var s=sp.getBoundingClientRect(), p=pr.getBoundingClientRect();
          return {spriteH:s.height, spriteTop:s.top, spriteBottom:s.bottom,
                  propH:p.height, propTop:p.top, propBottom:p.bottom,
                  stageH:st.height, stageX:st.left, stageW:st.width};})(__JS__)""".replace('__JS__', js))
        time.sleep(0.45)
        seat_y = info['propBottom'] - PROP_GROUND_FRAC * info['propH'] - seat_px
        clip = (max(0, info['stageX'] - 40), max(0, min(info['spriteTop'],
                                                         info['propTop']) - 20),
                min(1200, info['stageW'] + 80), min(info['stageH'], 900))
        p = shot(b, os.path.join(SAT, 'alley_sz_%d.png' % round(m * 100)), clip)
        rows.append((m, p, g, info, hip, seat_y, fig, ppm))
        print('%.2f м: холст %.1f%%, проп h=%.1f%% bottom=%.1f%% left=%.1f%% | '
              'спрайт %.0f px, проп %.0f px (%.0f..%.0f) | бёдра %.0f, сиденье %.0f '
              '(разница %+.0f px = %+.1f см)'
              % (m, h_pct, g['ph'], g['pb'], g['pl'], info['spriteH'], info['propH'],
                 info['propTop'], info['propBottom'], hip, seat_y,
                 seat_y - hip, (seat_y - hip) / ppm * 100))
finally:
    b.close()

html = """<!doctype html><meta charset="utf-8">
<style>
 body{margin:0;background:#0b0d12;color:#e9eef7;font:15px/1.35 "Trebuchet MS",Verdana,sans-serif}
 .wrap{padding:14px 16px 20px}
 h1{font-size:19px;margin:0 0 8px;letter-spacing:.03em}
 .sub{color:#93a0b6;font-size:13px;margin:0 0 12px}
 figure{margin:0 0 14px}
 .fr{border:1px solid #2a3346;border-radius:8px;overflow:hidden;max-width:1200px}
 .fr img{display:block;width:100%}
 figcaption{margin-top:5px;font-size:13px;color:#c3cddd}
 b{color:#ffd278}
</style>
<div class="wrap"><h1>«Зарянка» · аллея: размер поэта на скамейке</h1>
<p class="sub">Живой движок, узел alley, стр. 1. Скамейка пересчитана под каждый размер:
спинка у ближнего торца 0.90 м, сиденье 0.45 м, земля = ступни поэта.</p>
__ROWS__
</div>"""
rows_html = ''.join(
    """<figure><div class="fr"><img src="%s"></div>
<figcaption><b>%.2f м сидя</b> · спрайт %.0f%% сцены · фигура %.0f px = %.0f см ·
сиденье на <b>%+.1f см</b> от бёдер</figcaption></figure>"""
    % (os.path.basename(p), m, g['h'], fig, fig / ppm * 100, (seat_y - hip) / ppm * 100)
    for m, p, g, info, hip, seat_y, fig, ppm in rows)
sheet = os.path.join(SAT, 'alley_size_sheet.html')
open(sheet, 'w', encoding='utf-8').write(html.replace('__ROWS__', rows_html))

b2 = Browser(1600, 900)
try:
    b2.send('Emulation.setDeviceMetricsOverride', width=1240, height=900,
            deviceScaleFactor=1, mobile=False)
    b2.navigate('http://127.0.0.1:%d/_sat/alley_size_sheet.html' % PORT)
    time.sleep(1.5)
    h = b2.js("document.body.scrollHeight")
    raw = shot(b2, os.path.join(SAT, 'alley_size_sheet.png'), (0, 0, 1240, min(h, 3400)))
    # для показа в вебе — компактный JPEG (PNG 1.5 МБ в репо ни к чему)
    from PIL import Image as _Im
    im = _Im.open(raw)
    im = im.resize((1100, round(im.height * 1100 / im.width)), _Im.LANCZOS)
    out_dir = os.path.join(HERE, 'vn2', 'sheet')
    os.makedirs(out_dir, exist_ok=True)
    jp = os.path.join(out_dir, 'alley_size.jpg')
    im.convert('RGB').save(jp, 'JPEG', quality=84, optimize=True, progressive=True)
    print('лист: _sat/alley_size_sheet.png (%s px) -> vn2/sheet/alley_size.jpg %d Б'
          % (h, os.path.getsize(jp)))
finally:
    b2.close()
