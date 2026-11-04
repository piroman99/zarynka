# -*- coding: utf-8 -*-
"""Pages догнал сборку? Сверяем md5 vn2/img/cg/rec_35.webp локально и на демо."""
import hashlib
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(HERE, 'vn2', 'img', 'cg', 'rec_35.webp')
URL = 'https://piroman99.github.io/zarynka/vn2/img/cg/rec_35.webp?cb=%d'

with open(LOCAL, 'rb') as f:
    lm = hashlib.md5(f.read()).hexdigest()
print('локально %s  %d B' % (lm[:10], os.path.getsize(LOCAL)), flush=True)

for i in range(9):
    try:
        with urllib.request.urlopen(URL % int(time.time()), timeout=30) as r:
            data = r.read()
        rm = hashlib.md5(data).hexdigest()
        print('попытка %d: %s %d B %s' % (i + 1, rm[:10], len(data),
                                          'OK' if rm == lm else 'старое'), flush=True)
        if rm == lm:
            print('Pages отдаёт новую сборку')
            break
    except Exception as e:
        print('попытка %d: %s' % (i + 1, str(e)[:160]), flush=True)
    time.sleep(20)
