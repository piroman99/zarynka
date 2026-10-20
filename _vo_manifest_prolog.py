#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Дописываем в манифест озвучки 12 файлов пролога (их делал _vn2_vo.py,
поэтому в манифесте не было ни голоса, ни текста). Голос — закадр Charon."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VN2 = os.path.join(HERE, 'vn2')
VD = os.path.join(VN2, 'audio', 'vo')
MAN = os.path.join(VD, '_voices.json')

man = json.load(open(MAN, encoding='utf-8'))
src = open(os.path.join(VN2, 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('{'):src.rindex('}') + 1])

add = 0
for nd in D['nodes']:
    for pg in nd.get('pages') or []:
        vo = pg.get('vo')
        if not vo:
            continue
        who = pg.get('who') or 'narr'
        rec = man.setdefault(vo, {})
        rec.setdefault('voice', who)
        rec.setdefault('model', 'gemini-3.8-flash-tts')
        rec.setdefault('chars', len(pg['tx']))
        rec.setdefault('text', pg['tx'])
        add += 1
json.dump(man, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('дописано записей: %d, всего в манифесте: %d' % (add, len(man)))
