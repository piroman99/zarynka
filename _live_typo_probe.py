# -*- coding: utf-8 -*-
"""Проверка: я в сообщении дал ссылку с опечаткой (zaryanka вместо zarynka)?"""
import urllib.request

for u in ('https://piroman99.github.io/zaryanka/vn2/',
          'https://piroman99.github.io/zarynka/vn2/'):
    try:
        r = urllib.request.urlopen(u, timeout=40)
        print(r.status, len(r.read()), u)
    except Exception as e:
        print('ERR', getattr(e, 'code', ''), u)
