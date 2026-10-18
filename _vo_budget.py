# -*- coding: utf-8 -*-
"""Смета голосов: сколько знаков озвучивать по ролям (закадр / Старик / Сергей / Катя)."""
import os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

PRICE = 1.70 / 1000.0
tot = {}
per = []
for nd in D['nodes']:
    if nd['t'] != 'scene':
        continue
    for pg in nd['pages']:
        who = pg.get('who') or 'ЗАКАДР'
        tx = re.sub(r'^[\u2014\u2013-]+\s*', '', pg['tx'].strip())
        tot[who] = tot.get(who, 0) + len(tx)
        per.append((nd['id'], who, len(tx), pg.get('vo')))

print('%-12s %6s %8s' % ('роль', 'знаков', '₽'))
for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
    print('%-12s %6d %8.2f' % (k, v, v * PRICE))
allc = sum(tot.values())
print('%-12s %6d %8.2f' % ('ВСЕГО', allc, allc * PRICE))
print()
print('--- реплики по узлам ---')
for nid, who, n, vo in per:
    if who != 'ЗАКАДР':
        print(' %-10s %-10s %4d зн.  %s' % (nid, who, n, vo))
