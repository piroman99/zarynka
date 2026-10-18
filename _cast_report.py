# -*- coding: utf-8 -*-
"""Сводка по собранному content.js: каст по страницам приёмной + голоса."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
print('chars:', json.dumps(D['chars'], ensure_ascii=False))
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
print('страниц:', len(rec['pages']))
for i, p in enumerate(rec['pages']):
    c = p.get('cast') or {}
    print('%02d who=%-10s l=%-18s r=%-18s speak=%-10s | %s'
          % (i, p.get('who', '-'),
             '/'.join(c['l']) if c.get('l') else '-',
             '/'.join(c['r']) if c.get('r') else '-',
             c.get('speak', '-'), p['tx'][:46]))
