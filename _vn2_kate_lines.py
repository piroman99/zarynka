# -*- coding: utf-8 -*-
"""Реплики Екатерины (прямая речь) из content.js — выбрать строку для голосового теста."""
import os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'vn2', 'content.js'), encoding='utf-8').read()
D = json.loads(src[src.index('=') + 1:].strip().rstrip(';'))
i = 0
for nd in D['nodes']:
    if nd['t'] != 'scene':
        continue
    for pg in nd['pages']:
        if pg.get('who') == 'Екатерина':
            i += 1
            print('%2d  [%3d зн.] %s' % (i, len(pg['tx']), pg['tx']))
