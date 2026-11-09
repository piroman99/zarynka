# -*- coding: utf-8 -*-
"""Пробник: отвечает ли локальный сервер новеллы и с каким кодом."""
import sys
import urllib.request
import urllib.error

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
paths = ['/vn2/index.html', '/vn2/style.css', '/vn2/app.js',
         '/vn2/audio/vo/s1_00.mp3?v=7', '/out/znak3d_rot.mp4']
for p in paths:
    url = 'http://127.0.0.1:%d%s' % (PORT, p)
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            data = r.read()
            print('%s -> %s %d B %s' % (p, r.status, len(data), r.headers.get('Content-Type')))
    except urllib.error.HTTPError as e:
        print('%s -> HTTP %s' % (p, e.code))
    except Exception as e:
        print('%s -> ОШИБКА %r' % (p, e))
