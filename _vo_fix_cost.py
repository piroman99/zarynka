# -*- coding: utf-8 -*-
"""Смета починки: сколько символов надо переозвучить по каждому голосу."""
import os, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
VD = os.path.join(HERE, 'vn2', 'audio', 'vo')
man = json.load(open(os.path.join(VD, '_voices.json'), encoding='utf-8'))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
PRICE = {'narr': 1.70, 'Старик': 1.70, 'Сергей': 1.70, 'Екатерина': 10.84}


def md5(p):
    with open(p, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


need = []
for nd in D['nodes']:
    for i, pg in enumerate(nd.get('pages', [])):
        vo = pg.get('vo')
        if not vo:
            continue
        rec = man.get(vo, {})
        p = os.path.join(VD, os.path.basename(vo))
        bad = (rec.get('price') == 0 or rec.get('reused_from')
               or not os.path.exists(p))
        if bad:
            need.append((nd.get('id') or nd.get('t'), i, os.path.basename(vo),
                         rec.get('voice') or pg.get('who'), len(rec.get('text') or '')))

by = {}
for _, _, _, voice, n in need:
    by[voice] = by.get(voice, 0) + n
print('к переозвучке: %d файлов' % len(need))
tot = 0.0
for v, n in sorted(by.items(), key=lambda x: -x[1]):
    c = n * PRICE.get(v, 1.7) / 1000
    tot += c
    print('  %-10s %5d зн.  %6.2f ₽' % (v, n, c))
print('итого ~%.2f ₽' % tot)
for r in need:
    print('   ', r)
