# -*- coding: utf-8 -*-
"""Сколько знаков закадра в прологе и приёмной (смета смены голоса закадра)."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
pr = sum(len(p['tx']) for n in D['nodes'] if n.get('id', '').startswith('s')
         for p in n.get('pages', []))
rec = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
nr = sum(len(p['tx']) for p in rec['pages'] if not p.get('who'))
print('пролог: %d зн. -> %.2f ₽' % (pr, pr * 1.70 / 1000))
print('приёмная закадр: %d зн. -> %.2f ₽' % (nr, nr * 1.70 / 1000))
print('всего: %.2f ₽' % ((pr + nr) * 1.70 / 1000))
