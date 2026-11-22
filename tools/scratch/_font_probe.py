# -*- coding: utf-8 -*-
"""Есть ли fonttools/brotli (для WOFF2-подмножеств) и где лежат нужные шрифты."""
import os, sys, glob

for mod in ('fontTools', 'brotli', 'zopfli'):
    try:
        m = __import__(mod)
        print(mod, 'OK', getattr(m, 'version', ''))
    except Exception as e:
        print(mod, 'НЕТ', type(e).__name__, e)

cands = [
    '/usr/share/fonts/opentype/urw-base35/URWGothic-Demi.otf',
    '/usr/share/fonts/opentype/urw-base35/URWGothic-Book.otf',
    '/usr/share/fonts/truetype/lato/Lato-Bold.ttf',
    '/usr/share/fonts/truetype/lato/Lato-Regular.ttf',
]
for c in cands:
    print(('ЕСТЬ ' if os.path.exists(c) else 'НЕТ  '), c,
          (os.path.getsize(c) if os.path.exists(c) else ''))
