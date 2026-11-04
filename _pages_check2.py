# -*- coding: utf-8 -*-
"""Проверка живого демо: CG-картинка и app.js доступны с Pages."""
import time
import urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/'
for path in ('img/cg/rec_48.webp', 'app.js', 'style.css'):
    for attempt in range(6):
        try:
            with urllib.request.urlopen('%s%s?cb=%d' % (BASE, path, time.time()),
                                       timeout=30) as r:
                data = r.read()
            print('%-22s %d байт, код %s' % (path, len(data), r.status))
            break
        except Exception as e:
            print('%-22s %s' % (path, e))
            time.sleep(15)
