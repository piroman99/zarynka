# -*- coding: utf-8 -*-
"""ЛИСТ ДЛЯ ИВАНА: пропорции сидящего поэта к скамейке + под каким углом стоит скамейка.

Всё снято ЖИВЫМ движком (headless Chromium, сцена «аллея», 1600x900), не нарисовано:
  • ряд 1 — поэт тем же спрайтом при 100 / 130 / 140 / 150 % нынешнего размера;
    на каждом кадре жёлтая линия сиденья (50 % высоты пропа) и белая линия макушки;
  • ряд 2 — скамейка повёрнута на 0 / −6 / −10 / −15° + кадр «фон без пропа»,
    чтобы видеть, есть ли под пропом вторая нарисованная скамейка.

Считаем масштаб по Кейт (стоит, 1.70 м): px/м берём из её фигуры в этом же кадре.

Выход: _sat/alley_bench_poet_sheet.png (+ отдельные кадры в _sat/alley_*.png)
"""
import os
import sys
import time
import threading
import functools
import http.server
import socketserver
import base64

HERE = os.path.dirname(os.path.abspath(__file__))

ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _cdp import Browser
from _vn2_nodes import node_index

N = node_index('alley')
SAT = os.path.join(ROOT, '_sat')
os.makedirs(SAT, exist_ok=True)

# --- геометрия, снятая отдельным замером (_alley_probe_geom.py) ---
STAGE = {'x': 127, 'y': 0, 'w': 1346, 'h': 757}
PROP = {'x': -89, 'y': 356, 'w': 1025, 'h': 447}     # в координатах сцены
PROP_PAGE = {'x': STAGE['x'] + PROP['x'], 'y': STAGE['y'] + PROP['y'],
             'w': PROP['w'], 'h': PROP['h']}
POET_CANVAS_H = 568.0      # 75 % сцены при scale 1.0
SPRITE_BOTTOM = STAGE['y'] + STAGE['h'] + 0.03 * STAGE['h']   # bottom:-3%
FIG_TOP_FRAC = 0.287       # poet_seat_upset: верхнее поле 28.7 % холста
FIG_FILL = 0.704           # доля холста, занятая фигурой (upset)
SEAT_Y = PROP_PAGE['y'] + 0.50 * PROP_PAGE['h']    # линия сиденья по альфе пропа
KATE_FIG_H = 749.0 * 0.985                          # фигура Кейт в кадре, px
PX_PER_M = KATE_FIG_H / 1.70                        # масштаб кадра, px/м

print('масштаб по Кейт: %.0f px/м' % PX_PER_M)
print('линия сиденья (page y): %.0f' % SEAT_Y)


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(H, directory=HERE))
srv.handle_error = lambda *a: None
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d/vn2/index.html' % PORT
URL = BASE + '?node=%d&page=0&instant=1&text=1&voice=0&music=0&auto=0' % N


def shot_clip(b, path, x, y, w, h):
    r = b.send('Page.captureScreenshot', format='png',
               clip={'x': x, 'y': y, 'width': w, 'height': h, 'scale': 1})
    open(path, 'wb').write(base64.b64decode(r['data']))
    return path


POET_CROP = (250, 150, 900, 700)      # x, y, w, h в координатах страницы
BENCH_CROP = (0, 320, 1080, 520)

variants_poet = []
variants_bench = []

b = Browser(1600, 900)
try:
    b.navigate(URL)
    time.sleep(2.0)
    # проверим, что сцена та и спрайты на месте
    info = b.js("""(function(){var s=document.querySelectorAll('#cast .sprite');
      return {node:document.querySelector('#stage').className,
              poet:s[0].getAttribute('src'), poetOn:s[0].classList.contains('on'),
              prop:document.querySelector('#props .prop').getAttribute('src')};})()""")
    print('сцена:', info)

    # ---------- ряд 1: масштаб поэта ----------
    for s in (1.0, 1.3, 1.4, 1.5):
        b.js("""(function(){var e=document.querySelectorAll('#cast .sprite')[0];
          e.style.height='%d%%';})()""" % round(75 * s))
        time.sleep(0.35)
        p = shot_clip(b, os.path.join(SAT, 'alley_poet_%03d.png' % round(s * 100)), *POET_CROP)
        h_canvas = 0.75 * STAGE['h'] * s
        fig_top = SPRITE_BOTTOM - h_canvas + FIG_TOP_FRAC * h_canvas
        fig_h = FIG_FILL * h_canvas
        variants_poet.append({
            'file': os.path.basename(p), 'scale': s,
            'fig_h_px': fig_h, 'fig_cm': 100.0 * fig_h / PX_PER_M,
            'head_y': fig_top - POET_CROP[1], 'seat_y': SEAT_Y - POET_CROP[1],
            'crop_h': POET_CROP[3],
        })
        print('поэт %d%%: фигура %.0f px = %.0f см, макушка y=%.0f (в кропе)'
              % (round(s * 100), fig_h, 100.0 * fig_h / PX_PER_M, fig_top - POET_CROP[1]))
    b.js("""(function(){var e=document.querySelectorAll('#cast .sprite')[0];
      e.style.height='75%';})()""")

    # ---------- ряд 2: угол скамейки ----------
    # сначала фон БЕЗ пропа — видно ли под ним нарисованную скамейку
    b.js("document.querySelector('#props .prop').classList.remove('on')")
    time.sleep(0.4)
    p = shot_clip(b, os.path.join(SAT, 'alley_bench_noprop.png'), *BENCH_CROP)
    variants_bench.append({'file': os.path.basename(p), 'label': 'фон без пропа',
                           'deg': None})
    b.js("document.querySelector('#props .prop').classList.add('on')")

    for deg in (0, -6, -10, -15):
        b.js("""(function(){var e=document.querySelector('#props .prop');
          e.style.transform='translateX(-50%%) rotate(%ddeg)';})()""" % deg)
        time.sleep(0.35)
        p = shot_clip(b, os.path.join(SAT, 'alley_bench_%d.png' % abs(deg)), *BENCH_CROP)
        variants_bench.append({'file': os.path.basename(p), 'label': '%d°' % deg, 'deg': deg})
        print('скамейка %d°' % deg)
    b.js("""(function(){var e=document.querySelector('#props .prop');
      e.style.transform='translateX(-50%) rotate(0deg)';})()""")

    # ---------- собираем HTML-лист ----------
    def poet_panel(v):
        head = v['head_y'] / v['crop_h'] * 100
        seat = v['seat_y'] / v['crop_h'] * 100
        return """<figure class="p">
  <div class="fr"><img src="%s">
    <i class="ln seat" style="top:%.2f%%"></i>
    <i class="ln head" style="top:%.2f%%"></i>
    <b class="tag seat">сиденье</b><b class="tag head">макушка</b>
  </div>
  <figcaption><b>%d %%</b> · фигура %.0f px = <b>%.0f см</b></figcaption>
</figure>""" % (v['file'], seat, head, round(v['scale'] * 100), v['fig_h_px'], v['fig_cm'])

    def bench_panel(v):
        return """<figure class="p">
  <div class="fr"><img src="%s"></div>
  <figcaption><b>%s</b></figcaption>
</figure>""" % (v['file'], v['label'])

    html = """<!doctype html><meta charset="utf-8">
<style>
 body{margin:0;background:#0b0d12;color:#e9eef7;font:15px/1.35 "Trebuchet MS",Verdana,sans-serif}
 .wrap{padding:18px 20px 24px}
 h1{font-size:21px;margin:0 0 4px;letter-spacing:.04em}
 h2{font-size:16px;margin:18px 0 8px;color:#ffd278;letter-spacing:.05em}
 .sub{color:#93a0b6;font-size:13px;margin:0 0 6px}
 .row{display:flex;gap:12px;align-items:flex-start}
 .p{margin:0;flex:1}
 .fr{position:relative;border:1px solid #2a3346;border-radius:8px;overflow:hidden}
 .fr img{display:block;width:100%}
 .ln{position:absolute;left:0;right:0;height:0;border-top:2px dashed #ffd278;opacity:.9}
 .ln.head{border-top:2px solid #ffffff;opacity:.85}
 .tag{position:absolute;right:4px;font-size:11px;padding:1px 4px;border-radius:4px;
      background:rgba(0,0,0,.6);color:#ffd278}
 .tag.head{color:#fff}
 figcaption{margin-top:5px;font-size:12.5px;color:#c3cddd}
 .note{margin-top:14px;font-size:13px;color:#93a0b6;max-width:1500px}
</style>
<div class="wrap">
 <h1>«Зарянка» · сцена «аллея»: поэт и скамейка</h1>
 <p class="sub">Кадры сняты живым движком (headless Chromium, 1600×900, узел alley, стр. 1).
    Масштаб кадра по Кейт (1.70 м) = __PXPM__ px/м. Скамейка-проп 59 % сцены = 447 px,
    её сиденье — жёлтая линия. Рост сидящего мужчины ≈ 130–135 см.</p>

 <h2>1. Поэт тем же спрайтом: 100 / 130 / 140 / 150 % нынешнего</h2>
 <div class="row">__POET__</div>

 <h2>2. Скамейка: под каким углом она стоит (0° = как сейчас)</h2>
 <div class="row">__BENCH__</div>

 <p class="note">Первый кадр ряда 2 — фон БЕЗ пропа: там видно, есть ли под скамейкой
   вторая, нарисованная в самом фоне. Наклон указан в градусах против часовой стрелки.</p>
</div>"""
    html = (html.replace('__PXPM__', '%.0f' % PX_PER_M)
                .replace('__POET__', ''.join(poet_panel(v) for v in variants_poet))
                .replace('__BENCH__', ''.join(bench_panel(v) for v in variants_bench)))

    sheet = os.path.join(SAT, 'alley_sheet.html')
    open(sheet, 'w', encoding='utf-8').write(html)
    sheet_url = 'http://127.0.0.1:%d/_sat/alley_sheet.html' % PORT
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=1200,
           deviceScaleFactor=1, mobile=False)
    b.navigate(sheet_url)
    time.sleep(1.5)
    h = b.js("document.body.scrollHeight")
    print('высота листа:', h)
    chk = b.js("""(function(){
      var out=[], imgs=document.images;
      for(var i=0;i<imgs.length;i++){ if(!imgs[i].complete||imgs[i].naturalWidth===0)
        out.push('битая картинка '+imgs[i].src); }
      var figs=document.querySelectorAll('figure .fr');
      for(var i=0;i<figs.length;i++){ var r=figs[i].getBoundingClientRect();
        if(r.width<80||r.height<60) out.push('панель '+i+' мелкая '+Math.round(r.width)+'x'+Math.round(r.height)); }
      return {bad:out, n:document.querySelectorAll('figure').length};
    })()""")
    print('проверка листа:', chk)
    shot_clip(b, os.path.join(SAT, 'alley_bench_poet_sheet.png'), 0, 0, 1600, min(h, 2400))
    print('лист: _sat/alley_bench_poet_sheet.png')
finally:
    b.close()
