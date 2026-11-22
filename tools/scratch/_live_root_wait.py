# -*- coding: utf-8 -*-
"""Дождаться, пока корень Pages начнёт отдавать редирект на vn2/ (задержка Pages ~100 с)."""
import time
import urllib.request

URL = 'https://piroman99.github.io/zarynka/'
for i in range(1, 13):
    try:
        r = urllib.request.urlopen(urllib.request.Request(URL, headers={'Cache-Control': 'no-cache'}),
                                   timeout=40)
        txt = r.read().decode('utf-8', 'replace')
        target = 'vn2/' if 'url=vn2/' in txt else ('vn/' if 'url=vn/' in txt else '?')
        print('попытка %2d: редирект на %s' % (i, target))
        if target == 'vn2/':
            print('корень Pages ведёт на актуальную сборку')
            break
    except Exception as e:
        print('попытка %d: %s' % (i, str(e)[:100]))
    time.sleep(20)
