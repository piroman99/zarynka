# -*- coding: utf-8 -*-
"""Проверка, что музыка аллеи отдаётся с демо (Pages)."""
import urllib.request

BASE = 'https://piroman99.github.io/zarynka/assets/audio/sketch/'
for name in ('alley_mix.mp3', 'alley_bed.mp3', 'alley_amb.mp3'):
    try:
        req = urllib.request.Request(BASE + name, headers={'User-Agent': 'chk'})
        with urllib.request.urlopen(req, timeout=30) as r:
            n = 0
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                n += len(chunk)
        print(name, r.status, n)
    except Exception as e:  # noqa: BLE001
        print(name, 'ERR', str(e)[:80])
