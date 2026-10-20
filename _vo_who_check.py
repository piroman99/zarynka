# -*- coding: utf-8 -*-
"""Сверка «кто говорит на странице» (pg.who) с голосом, которым реально
озвучен её файл (манифест _voices.json -> voice)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VD = os.path.join(HERE, 'vn2', 'audio', 'vo')
man = json.load(open(os.path.join(VD, '_voices.json'), encoding='utf-8'))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('{'):src.rindex('}') + 1])

bad = 0
for n in D['nodes']:
    nid = n.get('id') or n.get('t')
    for k, pg in enumerate(n.get('pages') or []):
        vo = pg.get('vo')
        if not vo:
            continue
        rec = man.get(vo, {})
        want = pg.get('who') or 'narr'
        got = rec.get('voice')
        if got is None:
            print('?  %s[%d] %s: в манифесте нет голоса' % (nid, k, vo))
            bad += 1
        elif got != want:
            print('!! %s[%d] %s: на странице %s, в файле %s | %s'
                  % (nid, k, vo, want, got, pg['tx'][:60]))
            bad += 1
print('расхождений: %d' % bad)
