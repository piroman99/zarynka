# -*- coding: utf-8 -*-
"""Печать страниц узла «аллея» из content.js: индекс, bg, cast, первые 40 симв."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _vn2_nodes import node_index  # noqa: E402

src = open(os.path.join(ROOT, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(re.search(r'window\.VN\s*=\s*(\{.*\})\s*;?\s*$', src, re.S).group(1))
AL = node_index('alley')
nd = D['nodes'][AL]
print('alley = node=%d, pages=%d, bg=%r' % (AL, len(nd['pages']), nd.get('bg')))
for i in range(12, 22):
    p = nd['pages'][i]
    print('%2d bg=%-22s cast=%-28s %r'
          % (i, (p.get('bg') or '-'), json.dumps(p.get('cast'), ensure_ascii=False)[:28], (p.get('tx') or '')[:40]))
