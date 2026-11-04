# -*- coding: utf-8 -*-
"""Показать записи манифеста озвучки по префиксу имени файла.

    python3 _vo_show.py s1_ p6_
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, 'vn2', 'audio', 'vo', '_voices.json'), encoding='utf-8'))
pref = sys.argv[1:] or ['s1_']
for k in sorted(m):
    base = os.path.basename(k)
    if any(base.startswith(p) for p in pref):
        print('%-22s %3d зн.  %s' % (base, m[k].get('chars', 0), m[k].get('text', '')[:90]))
