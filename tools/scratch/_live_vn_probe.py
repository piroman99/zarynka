# -*- coding: utf-8 -*-
"""Куда ведёт корневой редирект и жив ли старый vn/ на Pages."""
import urllib.request

URLS = [
    'https://piroman99.github.io/zarynka/vn/',
    'https://piroman99.github.io/zarynka/vn/index.html',
    'https://piroman99.github.io/zarynka/vn2/index.html',
]
for u in URLS:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'Cache-Control': 'no-cache'}),
                                   timeout=40)
        print(r.status, '%7d B' % len(r.read()), r.geturl(), '<-', u)
    except Exception as e:
        print('ERR', getattr(e, 'code', ''), u, str(e)[:100])
