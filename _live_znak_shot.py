# -*- coding: utf-8 -*-
"""Живая демка: значок реально играет с нового файла на Pages."""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

URL = 'https://piroman99.github.io/zarynka/vn2/index.html?node=1&preload=0'
R = os.path.join(HERE, 'assets', 'review')

b = Browser(1600, 900)
try:
    b.navigate(URL)
    ok = b.wait_js("document.getElementById('znak') && document.getElementById('znak').videoWidth > 0",
                   timeout=90)
    time.sleep(1.2)
    info = b.js("""(function(){ var v=document.getElementById('znak');
      return [v.videoWidth, v.videoHeight, +v.duration.toFixed(2), v.paused?'pause':'play',
              (v.currentSrc||v.src||'').split('/').slice(-1)[0]]; })()""")
    print('живое видео:', info, '| дождались кадра:', ok)
    p = os.path.join(R, 'review_112_live_znak.png')
    b.shot(p)
    print('снимок:', os.path.basename(p))
    print('ошибки:', b.errors())
finally:
    b.close()
