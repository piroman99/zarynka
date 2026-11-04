# -*- coding: utf-8 -*-
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
i = src.index('window.VN =')
body = src[i:]
body = body[body.index('{'):].rstrip().rstrip(';')
D = json.loads(body)
for ni, node in enumerate(D['nodes']):
    pages = node.get('pages') or []
    if not pages:
        continue
    print('=== NODE', ni, node.get('id'), len(pages))
    for pi, p in enumerate(pages):
        who = p.get('who') or ''
        cast = p.get('cast') or {}
        ch = ','.join('%s:%s' % (k, (cast.get(k) or [''])[0][:4]) for k in ('l', 'r') if cast.get(k))
        print('%2d %-9s %-26s %s' % (pi, who, ch, (p.get('tx') or '')[:100]))
