# -*- coding: utf-8 -*-
"""Проверка путей, которые реально стоят в content.js (они идут от корня репозитория, не vn2)."""
import urllib.request

URLS = [
    'https://piroman99.github.io/zarynka/assets/audio/sketch/prolog_bed_soft_0.mp3',
    'https://piroman99.github.io/zarynka/assets/audio/sketch/vn_reception_soft_0.mp3',
    'https://piroman99.github.io/zarynka/out/znak3d_rot.mp4',
    'https://piroman99.github.io/zarynka/out/avm_v3_epic.mp4',
    'https://piroman99.github.io/zarynka/vn2',
    'https://piroman99.github.io/zarynka/vn2/',
    'https://piroman99.github.io/zarynka',
]
for u in URLS:
    req = urllib.request.Request(u, headers={'Cache-Control': 'no-cache'})
    try:
        r = urllib.request.urlopen(req, timeout=40)
        print(r.status, '%9d B' % len(r.read()), r.geturl(), '<-', u)
    except Exception as e:
        print('ERR', getattr(e, 'code', ''), u, str(e)[:120])
