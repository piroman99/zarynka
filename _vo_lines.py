# -*- coding: utf-8 -*-
"""Первые реплики каждого персонажа из content.js (для проб голоса)."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('window.VN =') + len('window.VN ='):].rstrip().rstrip(';'))
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
seen = set()
for i, pg in enumerate(rec['pages']):
    who = pg.get('who')
    if who and who not in seen:
        seen.add(who)
        print('%-10s p%-3d %s' % (who, i, pg['tx']))
