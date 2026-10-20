# -*- coding: utf-8 -*-
"""Пометить копии-каскад как stale_reason, чтобы _vn2_vo_cast.py их переозвучил."""
import os, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
VD = os.path.join(HERE, 'vn2', 'audio', 'vo')
MAN = os.path.join(VD, '_voices.json')
man = json.load(open(MAN, encoding='utf-8'))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))


def md5(p):
    with open(p, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


marked = 0
for nd in D['nodes']:
    for pg in nd.get('pages', []):
        vo = pg.get('vo')
        if not vo:
            continue
        rec = man.get(vo, {})
        if rec.get('price') == 0 or rec.get('reused_from'):
            rec['stale_reason'] = 'копия из старой сборки (каскад, баг 2026-10-20)'
            man[vo] = rec
            marked += 1
json.dump(man, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('помечено: %d' % marked)
