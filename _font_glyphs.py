# -*- coding: utf-8 -*-
"""Есть ли в woff2-сабсетах движка нужные глифы (Ё, —, !, ?, «») и все символы из content.js."""
import os
import json
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, 'vn2', 'fonts')
print('шрифты:', sorted(os.listdir(FONTS)) if os.path.isdir(FONTS) else 'нет каталога')

src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

chars = set()
for nd in D['nodes']:
    for pg in nd.get('pages', []):
        for it in (pg.get('ovl') or []):
            if 't' in it:
                chars |= set(it['t'])
print('символы титр-слоя:', ''.join(sorted(chars)))

for fn in sorted(os.listdir(FONTS)):
    if not fn.endswith('.woff2'):
        continue
    f = TTFont(os.path.join(FONTS, fn))
    cmap = set()
    for t in f['cmap'].tables:
        cmap |= set(t.cmap.keys())
    missing = sorted(c for c in chars if ord(c) not in cmap)
    print('%-28s глифов=%d  нет: %s' % (fn, len(cmap),
                                        ''.join(missing) if missing else '—'))
