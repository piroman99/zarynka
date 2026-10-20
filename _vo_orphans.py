# -*- coding: utf-8 -*-
"""Какие vo-файлы лежат в vn2/audio/vo, но ни одной страницей не используются."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VD = os.path.join(HERE, 'vn2', 'audio', 'vo')
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('{'):src.rindex('}') + 1])

used = set()
for nd in D['nodes']:
    for pg in nd.get('pages') or []:
        if pg.get('vo'):
            used.add(os.path.basename(pg['vo']))
allf = {f for f in os.listdir(VD) if f.endswith('.mp3')}
print('файлов: %d, используется: %d' % (len(allf), len(used)))
orph = sorted(allf - used)
print('сироты (%d): %s' % (len(orph), ', '.join(orph) or '-'))
man = json.load(open(os.path.join(VD, '_voices.json'), encoding='utf-8'))
extra = [k for k in man if os.path.basename(k) not in used]
print('лишних записей в манифесте: %d' % len(extra))
