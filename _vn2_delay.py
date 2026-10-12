# -*- coding: utf-8 -*-
"""Расчёт текущей задержки авто по страницам (по длине текста)."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))

AUTO_BASE, AUTO_PER_CHAR = 450, 20
CAP = 1900
rows = []
for nd in D['nodes']:
    if nd['t'] != 'scene':
        continue
    for i, pg in enumerate(nd['pages']):
        n = len(pg['tx'])
        d = AUTO_BASE + min(CAP, n * AUTO_PER_CHAR)
        rows.append((nd['id'], i, n, d / 1000.0))

print('страниц:', len(rows))
print('сек/стр: min=%.2f  max=%.2f  сред=%.2f' % (
    min(r[3] for r in rows), max(r[3] for r in rows), sum(r[3] for r in rows) / len(rows)))
import collections
buck = collections.Counter()
for _, _, n, d in rows:
    buck[round(d * 2) / 2] += 1
for k in sorted(buck):
    print('  ~%.1f с : %d стр' % (k, buck[k]))
print('\nпо узлам:')
agg = collections.defaultdict(list)
for sid, i, n, d in rows:
    agg[sid].append(d)
for sid in agg:
    print('  %-9s стр=%2d  сумма=%5.1f с  сред=%.1f с' % (sid, len(agg[sid]), sum(agg[sid]), sum(agg[sid]) / len(agg[sid])))
print('ВСЕГО авто: %.1f с (%.1f мин)' % (sum(r[3] for r in rows), sum(r[3] for r in rows) / 60))
