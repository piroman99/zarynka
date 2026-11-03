# -*- coding: utf-8 -*-
"""Показать манифест голосов vn2/audio/vo/_voices.json (только чтение)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'vn2', 'audio', 'vo', '_voices.json')
d = json.load(open(p, encoding='utf-8'))
print(type(d), len(d))
ks = list(d)[:6]
print(ks)
print(json.dumps({k: d[k] for k in ks}, ensure_ascii=False)[:600])
pro = [k for k in d if str(k).startswith(('s1', 's2', 'p6'))]
print('prolog keys:', pro[:12])
