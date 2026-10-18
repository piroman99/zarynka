# -*- coding: utf-8 -*-
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
nd = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
for i in (10, 11, 12, 24, 25, 26, 27, 41, 42, 43, 44, 47, 48):
    print(i, '|', nd['pages'][i]['tx'])
    print()
