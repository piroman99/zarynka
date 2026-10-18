# -*- coding: utf-8 -*-
"""Показать первые реплики каждого персонажа в Приёмной."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
nd = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
seen = set()
for i, pg in enumerate(nd['pages']):
    who = pg.get('who')
    if who and who not in seen:
        seen.add(who)
        print(i, who, '|', pg['tx'])
        print()
