# -*- coding: utf-8 -*-
"""Живая проверка: Pages отдаёт новый s4.webp."""
import os
import hashlib
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(HERE, 'vn2', 'img', 'prolog', 's4.webp')
URL = 'https://piroman99.github.io/zarynka/vn2/img/prolog/s4.webp'
data = open(LOCAL, 'rb').read()
print('локально:', len(data), 'B  md5', hashlib.md5(data).hexdigest())
for attempt in range(6):
    try:
        req = urllib.request.Request(URL, headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
            code = r.status
        same = hashlib.md5(body).hexdigest() == hashlib.md5(data).hexdigest()
        print('попытка %d: HTTP %s, %d B, совпал с локальным: %s' % (attempt + 1, code, len(body), same))
        if same:
            break
    except Exception as e:
        print('попытка %d: ошибка %s' % (attempt + 1, e))
    import time
    time.sleep(20)
