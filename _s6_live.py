# -*- coding: utf-8 -*-
"""Pages отдаёт обновления с задержкой ~100 с: ждём, пока s6.webp на демо совпадёт с локальным."""
import hashlib
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
local = os.path.join(HERE, 'vn2', 'img', 'prolog', 's6.webp')
want = hashlib.md5(open(local, 'rb').read()).hexdigest()
size = os.path.getsize(local)
print('локально:', size, 'B md5', want)

url = 'https://piroman99.github.io/zarynka/vn2/img/prolog/s6.webp'
for i in range(1, 13):
    try:
        req = urllib.request.Request(url + '?cb=%d' % int(time.time()),
                                     headers={'Cache-Control': 'no-cache'})
        data = urllib.request.urlopen(req, timeout=60).read()
        h = hashlib.md5(data).hexdigest()
        print('попытка %2d: %d B md5 %s %s' % (i, len(data), h, 'СОВПАЛО' if h == want else 'старый'))
        if h == want:
            print('Pages отдаёт новый кадр')
            break
    except Exception as e:
        print('попытка %d: ошибка %s' % (i, str(e)[:120]))
    time.sleep(20)
