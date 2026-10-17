# -*- coding: utf-8 -*-
"""Проверка ЖИВОЙ демки на GitHub Pages: предзагрузка, её время, снимки титула и S1."""
import os, sys, time, hashlib, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

BASE = 'https://piroman99.github.io/zarynka/vn2/'

# 1) app.js на Pages = локальный?
local = open(os.path.join(HERE, 'vn2', 'app.js'), 'rb').read()
lh = hashlib.sha256(local).hexdigest()[:16]
req = urllib.request.Request(BASE + 'app.js', headers={'User-Agent': 'nanobot', 'Cache-Control': 'no-cache'})
try:
    remote = urllib.request.urlopen(req, timeout=60).read()
    rh = hashlib.sha256(remote).hexdigest()[:16]
    print('app.js локально', lh, '| Pages', rh, '->', 'СОВПАДАЕТ' if lh == rh else 'Pages ещё старый')
except Exception as e:
    print('app.js fetch FAIL', type(e).__name__, e)

b = Browser(1600, 900)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=1600, height=900, deviceScaleFactor=1, mobile=False)
    import threading
    holder = {}

    def nav():
        b.navigate(BASE)

    t_all = time.time()
    nav()
    time.sleep(0.3)
    shots = 0
    done = False
    while time.time() - t_all < 180:
        st = b.js("(function(){var e=document.getElementById('pltext'),p=document.getElementById('pl');"
                  "return (e?e.textContent:'')+'|'+(p&&p.classList.contains('done')?'done':'')})()")
        if st and 'done' in st:
            done = True
            break
        time.sleep(2)
    print('предзагрузка на живой демке:', 'завершена за %.1f с' % (time.time() - t_all) if done else 'НЕ завершилась')
    print('кэши:', b.js("JSON.stringify({img: __PL.img.size, aud: __PL.aud.size, vid: __PL.vid.size, miss: __PL.miss.size})"))
    b.js("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(1))))")
    b.shot(os.path.join(HERE, 'assets', 'review', '_live_title.png'))

    b.js("document.getElementById('start').click()")
    ok = b.wait_js("!document.getElementById('vlayer').hidden", timeout=40)
    print('старт:', ok, '| znak.readyState', b.js("document.getElementById('znak').readyState"))
    b.js("document.getElementById('vskip').click()")
    time.sleep(1.2)
    print('голос blob:', str(b.js("document.getElementById('voice').getAttribute('src')"))[:46])
    print('фон:', b.js("(function(){var a=document.getElementById('bg-a'),c=document.getElementById('bg-b');return (a.classList.contains('on')?a:c).style.backgroundImage})()"))
    b.js("new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(1))))")
    b.shot(os.path.join(HERE, 'assets', 'review', '_live_s1.png'))
    print('ошибок JS:', len(b.errors()))
    for e in b.errors()[:5]:
        print('  ', e)
finally:
    b.close()
