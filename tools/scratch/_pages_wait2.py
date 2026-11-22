# -*- coding: utf-8 -*-
"""Ждём деплой GitHub Pages и проверяем, что на демо уже новый content.js (проп-скамейка)."""
import sys
import time
import urllib.request

URL = 'https://piroman99.github.io/zarynka/vn2/content.js'


def get(u, t=25):
    req = urllib.request.Request(u, headers={'Cache-Control': 'no-cache',
                                             'User-Agent': 'zaryanka-check'})
    with urllib.request.urlopen(req, timeout=t) as r:
        return r.read().decode('utf-8', 'replace')


deadline = time.time() + 420
n = 0
while time.time() < deadline:
    n += 1
    try:
        txt = get(URL + '?v=%d' % int(time.time()))
        has_prop = 'img/prop/bench.webp' in txt
        has_seat = 'poet_seat' in txt and '"seated": true' in txt
        has_music = 'alley_mix.mp3' in txt
        print('попытка %d: проп=%s сидящий=%s музыка=%s' % (n, has_prop, has_seat, has_music))
        if has_prop and has_seat and has_music:
            print('демо обновлено')
            sys.exit(0)
    except Exception as e:  # noqa: BLE001
        print('попытка %d: %s' % (n, str(e)[:90]))
    time.sleep(20)
print('демо не обновилось за отведённое время')
sys.exit(1)
