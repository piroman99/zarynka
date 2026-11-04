# -*- coding: utf-8 -*-
"""Печатает страницы приёмной из собранного content.js: индекс, состав, начало текста."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
m = re.search(r'=\s*(\{.*\})', src, re.S)
D = json.loads(m.group(1))
for i, nd in enumerate(D['nodes']):
    nid = nd.get('id') or nd.get('t')
    if nid != 'reception':
        continue
    print('node index', i, 'pages', len(nd['pages']))
    for j, pg in enumerate(nd['pages']):
        cast = pg.get('cast') or {}
        cs = ' '.join('%s=%s/%s' % (side, v[0], v[1]) for side, v in sorted(cast.items()))
        print('%2d [%-22s] %s' % (j, cs, (pg.get('tx') or '')[:70].replace('\n', ' ')))
