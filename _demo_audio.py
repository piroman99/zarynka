# -*- coding: utf-8 -*-
"""Размеры аудио в демо против локальных: доказательство, что демо показывает старое."""
import os, urllib.request

BASE = 'https://piroman99.github.io/zarynka/vn2/audio/vo/'
HERE = os.path.dirname(os.path.abspath(__file__))
LOC = os.path.join(HERE, 'vn2', 'audio', 'vo')
for nm in ('rec_00.mp3', 'rec_01.mp3', 'rec_10.mp3', 'rec_47.mp3', 'rec_50.mp3'):
    try:
        req = urllib.request.Request(BASE + nm, method='HEAD',
                                     headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, timeout=30)
        rem = r.headers.get('Content-Length')
    except Exception as e:
        rem = 'ERR %s' % e
    loc = os.path.getsize(os.path.join(LOC, nm))
    print('%-12s demo=%-10s local=%d %s' % (nm, rem, loc,
          '' if str(rem) == str(loc) else '  <-- РАЗНЫЕ'))
