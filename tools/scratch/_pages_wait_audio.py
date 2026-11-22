# -*- coding: utf-8 -*-
"""Ждём Pages и проверяем, что на демо новая музыка (content.js с ?v=2 и новый размер mp3)."""
import os
import sys
import time
import urllib.request

WANT_SIZE = os.path.getsize('assets/audio/sketch/alley_mix.mp3')
BASE = 'https://piroman99.github.io/zarynka/'


def fetch(u, head_only=False):
    req = urllib.request.Request(u, headers={'User-Agent': 'zaryanka-check',
                                             'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=30) as r:
        if head_only:
            return r.status, r.headers.get('Content-Length')
        return r.read()


deadline = time.time() + 540
n = 0
while time.time() < deadline:
    n += 1
    try:
        txt = fetch(BASE + 'vn2/content.js?t=%d' % int(time.time())).decode('utf-8', 'replace')
        has_v2 = 'alley_mix.mp3?v=2' in txt
        size = fetch(BASE + 'assets/audio/sketch/alley_mix.mp3?t=%d' % int(time.time()),
                     head_only=True)[1]
        print('попытка %d: ?v=2 %s, mp3 %s (ждём %d)' % (n, has_v2, size, WANT_SIZE), flush=True)
        if has_v2 and str(size) == str(WANT_SIZE):
            print('ДЕМО ОБНОВЛЕНО')
            sys.exit(0)
    except Exception as e:  # noqa: BLE001
        print('попытка %d: %s' % (n, str(e)[:90]), flush=True)
    time.sleep(20)
print('не дождались')
sys.exit(1)
