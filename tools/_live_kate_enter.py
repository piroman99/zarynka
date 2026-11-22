# -*- coding: utf-8 -*-
"""Живая проверка: Екатерина входит на описании (стр. 21) в демо на Pages."""
import json
import re
import urllib.request

URL = 'https://piroman99.github.io/zarynka/vn2/content.js?x=%d' % __import__('time').time()
src = urllib.request.urlopen(URL, timeout=30).read().decode('utf-8')
m = re.search(r'=\s*(\{.*\})', src, re.S)
D = json.loads(m.group(1))
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
for j in (2, 3, 4):
    pg = rec['pages'][j]
    cast = pg.get('cast') or {}
    print('%2d %-28s %s' % (j, ' '.join('%s=%s/%s' % (k, v[0], v[1]) for k, v in sorted(cast.items())),
                            (pg.get('tx') or '')[:46]))
ok = ('r' in (rec['pages'][3].get('cast') or {})) and ('r' not in (rec['pages'][2].get('cast') or {}))
print('ИТОГ:', 'живое демо с новым выходом' if ok else 'ДЕМО ЕЩЁ СТАРОЕ')
