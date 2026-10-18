# -*- coding: utf-8 -*-
"""Разбор Приёмной: кто сколько говорит + сколько знаков на каждый голос."""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

rec = [nd for nd in D['nodes'] if nd.get('id') == 'reception']
if not rec:
    print('нет узла reception'); sys.exit(1)
nd = rec[0]
print('страниц:', len(nd['pages']))
tot = {}
narr = 0
for pg in nd['pages']:
    who = pg.get('who') or '(закадр/автор)'
    n = len(pg['tx'])
    tot[who] = tot.get(who, 0) + n
s = sum(tot.values())
for k, v in sorted(tot.items(), key=lambda x: -x[1]):
    print('  %-16s %5d зн.' % (k, v))
print('всего %d зн. → ~%.2f ₽ (1.70 ₽/1000)' % (s, s * 1.7 / 1000))

# сколько страниц с прямой речью каждого
cnt = {}
for pg in nd['pages']:
    if pg.get('who'):
        cnt[pg['who']] = cnt.get(pg['who'], 0) + 1
print('реплик:', cnt)
