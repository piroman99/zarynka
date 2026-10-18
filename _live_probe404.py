# -*- coding: utf-8 -*-
"""Проверка живой демо-страницы: какие URL отдают 200, какие 404."""
import urllib.request

URLS = [
    'https://piroman99.github.io/zarynka/',
    'https://piroman99.github.io/zarynka/vn2/',
    'https://piroman99.github.io/zarynka/vn2/index.html',
    'https://piroman99.github.io/zarynka/vn2/app.js',
    'https://piroman99.github.io/zarynka/vn2/content.js',
    'https://piroman99.github.io/zarynka/vn2/style.css',
    'https://piroman99.github.io/zarynka/vn2/img/prolog/s6.webp',
    'https://piroman99.github.io/zarynka/vn2/manifest.webmanifest',
]

for u in URLS:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={'Cache-Control': 'no-cache'}),
                                   timeout=40)
        print(r.status, '%8d B' % len(r.read()), u)
    except Exception as e:
        print('ERR', getattr(e, 'code', ''), u, str(e)[:140])
