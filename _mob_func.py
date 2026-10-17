# -*- coding: utf-8 -*-
"""Функциональный тест мобильных правок: тап по подстрочнику, листание,
кинозал (тизер) в портрете, кнопка «полный экран» (реальный жест через CDP).
"""
import os, sys, json, time
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _cdp

URL = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
OUT = os.path.join(HERE, '.tmp_mob')
os.makedirs(OUT, exist_ok=True)
VP = [(390, 844, 2), (844, 390, 2)]

res = {}
b = _cdp.Browser(1600, 900)
try:
    for w, h, dpr in VP:
        tag = '%dx%d' % (w, h)
        b.send('Emulation.setDeviceMetricsOverride', width=w, height=h, deviceScaleFactor=dpr, mobile=True)
        b.navigate(URL + '?instant=1&text=1&voice=0&music=0&preload=0&node=2', wait=1.4)
        p0 = b.js('__DBG.pos')
        b.js('document.getElementById("box").click()')
        time.sleep(0.2)
        p1 = b.js('__DBG.pos')
        b.js('document.getElementById("stage").click()')
        time.sleep(0.2)
        p2 = b.js('__DBG.pos')
        # двойной клик по подстрочнику подряд (должен листать по одной)
        b.js('document.getElementById("box").click()')
        time.sleep(0.15)
        p3 = b.js('__DBG.pos')
        res[tag] = {'pos_start': p0, 'after_box_tap': p1, 'after_stage_tap': p2, 'after_2nd_tap': p3,
                    'tap_advances_one': (p1 == p0 + 1 and p2 == p1 + 1 and p3 == p2 + 1)}

        # --- кинозал из титула ---
        b.navigate(URL + '?instant=1&text=1&voice=0&music=0&preload=0', wait=1.2)
        b.js('document.getElementById("teaser").click()')
        time.sleep(1.8)
        cin = b.js("""(() => { const c = document.getElementById('cinema'), v = document.getElementById('avm');
          const r = c.getBoundingClientRect(), b = v.getBoundingClientRect();
          return {visible: !c.hidden, cinema: [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)],
                  video: [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height)],
                  vw: v.videoWidth, vh: v.videoHeight, paused: v.paused, t: +v.currentTime.toFixed(2),
                  chint: getComputedStyle(document.getElementById('chint')).display}; })()""")
        time.sleep(0.4)
        shot = os.path.join(OUT, 'func_cinema_%s.png' % tag)
        b.shot(shot)
        cin['shot'] = os.path.relpath(shot, HERE)
        cin['shot_bytes'] = os.path.getsize(shot)
        res[tag]['cinema'] = cin

        # выходим из кинозала
        b.js('document.getElementById("skip").click()')
        time.sleep(0.6)

        # --- кнопка «полный экран»: настоящий мышь-клик (нужен user gesture) ---
        fr = b.js("""(() => { const b = document.getElementById('t-full'); const r = b.getBoundingClientRect();
            return [Math.round(r.x + r.width/2), Math.round(r.y + r.height/2)]; })()""")
        b.send('Input.dispatchMouseEvent', type='mousePressed', x=fr[0], y=fr[1], button='left', clickCount=1)
        b.send('Input.dispatchMouseEvent', type='mouseReleased', x=fr[0], y=fr[1], button='left', clickCount=1)
        time.sleep(0.9)
        fs = b.js("""({fsEl: !!document.fullscreenElement, fsEnabled: !!document.fullscreenEnabled,
                     toast: document.getElementById('toast').className})""")
        res[tag]['fullscreen'] = fs
        if fs['fsEl']:
            b.js('document.exitFullscreen && document.exitFullscreen()')
            time.sleep(0.5)
finally:
    errs = [e for e in b.errors() if 'manifest' not in e and 'ERR_FAILED' not in e]
    b.close()

json.dump(res, open(os.path.join(OUT, 'func.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
print('errors:', errs)
