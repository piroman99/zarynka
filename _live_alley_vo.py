# -*- coding: utf-8 -*-
"""Живая проверка после пуша: на Pages лежит новый content.js и озвучка сцены."""
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


for rel in ('content.js', 'audio/vo/al_14.mp3', 'audio/vo/al_00.mp3'):
    live = get(rel)
    loc = open(os.path.join(HERE, 'vn2', rel), 'rb').read()
    print('%-22s live %8d  local %8d  %s' % (rel, len(live), len(loc),
                                             'совпало' if live == loc else 'РАЗНОЕ (Pages догоняет)'))

D = json.loads(re.search(r'=\s*(\{.*\})', get('content.js').decode('utf-8'), re.S).group(1))
print('voVer на демо:', D.get('voVer'))
al = [n for n in D['nodes'] if n.get('id') == 'alley'][0]
withvo = sum(1 for pg in al['pages'] if pg.get('vo'))
print('узел alley: страниц %d, с озвучкой %d' % (len(al['pages']), withvo))
st = [n for n in D['nodes'] if n.get('id') == 'steps'][0]
print('узел steps: страниц %d, с озвучкой %d'
      % (len(st['pages']), sum(1 for pg in st['pages'] if pg.get('vo'))))
