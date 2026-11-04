# -*- coding: utf-8 -*-
"""Страницы новой сцены «аллея у ворот»: индекс, состав, текст."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(re.search(r'=\s*(\{.*\})', src, re.S).group(1))
for i, nd in enumerate(D['nodes']):
    nid = nd.get('id')
    if nid not in ('steps', 'alley'):
        continue
    print('\n=== node %d %s (%d стр.) bg=%s trans=%s' % (i, nid, len(nd['pages']),
                                                        nd.get('bg'), nd.get('trans')))
    for j, pg in enumerate(nd['pages']):
        cast = pg.get('cast') or {}
        cs = ' '.join('%s=%s/%s' % (k, v[0], v[1]) for k, v in sorted(cast.items())
                      if k != 'speak')
        sp = (' speak=' + cast['speak']) if cast.get('speak') else ''
        print('%2d [%-34s]%s %s' % (j, cs, sp, (pg.get('tx') or '')[:58]))
