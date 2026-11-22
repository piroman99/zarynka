# -*- coding: utf-8 -*-
"""Что лежит в корне Pages (572 B) и в vn2/index.html — показать содержимое."""
import urllib.request

for u in ('https://piroman99.github.io/zarynka/', 'https://piroman99.github.io/zarynka/vn2/'):
    r = urllib.request.urlopen(u, timeout=40)
    txt = r.read().decode('utf-8', 'replace')
    print('=' * 70)
    print(u, r.status, len(txt), 'символов')
    print(txt[:1800])
