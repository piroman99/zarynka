# -*- coding: utf-8 -*-
"""Pages догнал фикс титр-слоя? Сверяем md5 app.js и STATUS не нужен — только vn2."""
import hashlib
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://piroman99.github.io/zarynka/vn2/'
FILES = ['app.js']


def md5_local(rel):
    with open(os.path.join(HERE, 'vn2', rel), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


local = {rel: md5_local(rel) for rel in FILES}
for rel in FILES:
    print('локально %-18s %s  %d B' % (rel, local[rel][:10],
                                       os.path.getsize(os.path.join(HERE, 'vn2', rel))),
          flush=True)

for i in range(12):
    ok = 0
    for rel in FILES:
        url = BASE + rel + '?cb=%d' % int(time.time() * 1000 + i)
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data = r.read()
            rm = hashlib.md5(data).hexdigest()
        except Exception as e:
            rm, data = 'ERR:%s' % e, b''
        same = rm == local[rel]
        ok += same
        print('попытка %2d  %-18s %s %6d B %s'
              % (i + 1, rel, rm[:10], len(data), 'OK' if same else 'старое'), flush=True)
    if ok == len(FILES):
        print('Pages отдаёт новую сборку')
        break
    time.sleep(15)