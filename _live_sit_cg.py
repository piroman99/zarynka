# -*- coding: utf-8 -*-
"""Живое демо: попали ли на Pages сидящий поэт и CG «Муза» (ba55d03)."""
import hashlib
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://piroman99.github.io/zarynka/vn2/'
q = int(time.time())


def get(rel):
    return urllib.request.urlopen(BASE + rel + '?x=%d' % q, timeout=30).read()


for rel in ('content.js', 'img/char/poet_sit.webp', 'img/cg/al_muza.webp'):
    try:
        live = get(rel)
    except Exception as e:  # noqa: BLE001
        print('%-26s НЕТ на Pages: %s' % (rel, e))
        continue
    loc = open(os.path.join(HERE, 'vn2', rel), 'rb').read()
    print('%-26s live %8d  local %8d  %s'
          % (rel, len(live), len(loc), 'совпало' if live == loc else 'РАЗНОЕ (Pages догоняет)'))

D = json.loads(re.search(r'=\s*(\{.*\})', get('content.js').decode('utf-8'), re.S).group(1))
chars = list(D['chars'])
print('\nперсонажи на демо:', chars)
al = [n for n in D['nodes'] if n.get('id') == 'alley'][0]
cgp = [i for i, pg in enumerate(al['pages']) if pg.get('cg')]
print('CG-страницы «аллеи» на демо:', cgp,
      [(i, (al['pages'][i].get('tx') or '')[:40]) for i in cgp])
used = sorted({(pg.get('cast') or {}).get('r', [None])[0] for pg in al['pages']
               if (pg.get('cast') or {}).get('r')})
print('правый спрайт в «аллее»:', used)
