# -*- coding: utf-8 -*-
"""Найти «чистые» реплики (без авторского текста) подлиннее — для теста голосов."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
nd = [n for n in D['nodes'] if n.get('id') == 'reception'][0]
for who in ('Старик', 'Сергей', 'Екатерина'):
    cands = []
    for i, pg in enumerate(nd['pages']):
        if pg.get('who') != who:
            continue
        tx = pg['tx'].strip()
        if not tx.startswith('—'):
            continue
        # «чистая» реплика: ровно одно тире (нет авторской вставки/продолжения)
        if tx.count('—') + tx.count('–') != 1:
            continue
        cands.append((len(tx), i, tx))
    cands.sort(reverse=True)
    print('==', who)
    for n, i, tx in cands[:3]:
        print('  p%-3d %4d | %s' % (i, n, tx))
    print()
