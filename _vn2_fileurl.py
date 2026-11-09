# -*- coding: utf-8 -*-
"""Проверка, что новелла открывается прямо из файла (file://) — без сервера.
Иван может ткнуть файл в своём браузере и проверить портрет через эмуляцию.
Смотрим: стартует ли, играет ли звук, нет ли ошибок загрузки."""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _cdp import Browser

URL = 'file://' + os.path.join(HERE, 'vn2', 'index.html')
print('URL:', URL)

b = Browser(390, 844)
try:
    b.send('Emulation.setDeviceMetricsOverride', width=390, height=844,
           deviceScaleFactor=2, mobile=True)
    b.navigate(URL)
    time.sleep(2.0)
    print('  старт-экран:', b.js("document.getElementById('title').classList.contains('show')"))
    print('  портретная вёрстка:', b.js("matchMedia('(max-aspect-ratio:1/1)').matches"))
    print('  ☰ виден:', b.js("getComputedStyle(document.getElementById('t-menu')).display"))
    b.js("document.getElementById('start').click()")
    time.sleep(2.0)
    print('  после «Начать»: узел', b.js("(window.__DBG&&__DBG.pos!==undefined)?__DBG.pos:null"))
    print('  кадр (bg) есть:', b.js("(function(){var s=document.querySelector('#stage .bg, #stage img');return !!s})()"))
    print('  голос/аудио: src', b.js("(document.querySelector('audio')||{}).src || null"))
    print('  sw зарегистрирован:', b.js("!!(navigator.serviceWorker&&navigator.serviceWorker.controller)||'n/a'"))
    print('  ошибки:', b.errors()[:6])
    b.shot(os.path.join(HERE, '_sat', 'tools_m_fileurl.png'))
finally:
    b.close()
