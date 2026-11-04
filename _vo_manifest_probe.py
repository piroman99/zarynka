# -*- coding: utf-8 -*-
"""Манифест озвучки: какие голоса записаны для новой сцены."""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, 'vn2', 'audio', 'vo', '_voices.json'), encoding='utf-8'))
ks = [k for k in m if 'al_' in k]
print('записей сцены «аллея»: %d' % len(ks))
print('по голосам:', dict(Counter(m[k].get('voice') for k in ks)))
for k in sorted(ks)[:3] + sorted(ks)[-2:]:
    print('  %-12s %-12s %s' % (k, m[k].get('voice'), (m[k].get('text') or '')[:44]))
print('\nвсего записей в манифесте:', len(m))
