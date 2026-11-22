# -*- coding: utf-8 -*-
"""Проверка, что GitHub Pages отдаёт новую сборку."""
import json
import time
import urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/'
for attempt in range(8):
    try:
        with urllib.request.urlopen(BASE + 'content.js?cachebust=%d' % time.time(),
                                    timeout=30) as r:
            txt = r.read().decode('utf-8')
        has_ded = '"ded"' in txt
        has_cg = 'img/cg/rec_48' in txt
        has_ivan = 'piroman99' in txt
        print('попытка %d: размер %d, ded=%s cg=%s piroman99=%s'
              % (attempt + 1, len(txt), has_ded, has_cg, has_ivan))
        if has_ded and has_cg and has_ivan:
            print('Pages отдаёт новую сборку')
            break
    except Exception as e:
        print('попытка %d: %s' % (attempt + 1, e))
    time.sleep(20)
